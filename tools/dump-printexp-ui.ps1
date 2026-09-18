# Lecture seule — aucun Invoke, aucun clic, aucun TB_PRESSBUTTON.
# Session console (bureau User), PrintExp ouvert.

$ErrorActionPreference = 'Continue'
$out = 'C:\Users\User\printexp-ui-dump.txt'
$lines = New-Object System.Collections.Generic.List[string]
function L($s) { $script:lines.Add([string]$s) }

L ("timestamp=" + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
L ("session=$([System.Diagnostics.Process]::GetCurrentProcess().SessionId)")

$proc = Get-Process -Name PrintExp_X64 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) {
  L 'ERROR: PrintExp_X64 not running'
  $lines | Set-Content -LiteralPath $out -Encoding UTF8
  exit 1
}
$hwndMain = [IntPtr]$proc.MainWindowHandle
L ("pid=$($proc.Id) session=$($proc.SessionId) title='$($proc.MainWindowTitle)' hwnd=$hwndMain")

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public class PeDumpWin32 {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr h, EnumProc p, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsWindowEnabled(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, StringBuilder l);
  [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, IntPtr l);
  public struct RECT { public int L, T, R, B; }
  public const int TB_GETBUTTONCOUNT = 0x0418;
  public const int TB_GETBUTTONTEXTW = 0x044B;
  public static string Txt(IntPtr h) {
    var sb = new StringBuilder(512);
    GetWindowText(h, sb, sb.Capacity);
    return sb.ToString();
  }
  public static string Cls(IntPtr h) {
    var sb = new StringBuilder(256);
    GetClassName(h, sb, sb.Capacity);
    return sb.ToString();
  }
}
"@

function Fmt-Hwnd([IntPtr]$h) {
  $cls = [PeDumpWin32]::Cls($h)
  $txt = [PeDumpWin32]::Txt($h)
  $id = [PeDumpWin32]::GetDlgCtrlID($h)
  $vis = [PeDumpWin32]::IsWindowVisible($h)
  $en = [PeDumpWin32]::IsWindowEnabled($h)
  $r = New-Object PeDumpWin32+RECT
  [void][PeDumpWin32]::GetWindowRect($h, [ref]$r)
  $par = [PeDumpWin32]::GetParent($h)
  return ("hwnd={0} parent={1} class='{2}' id={3} vis={4} en={5} rect={6},{7}-{8},{9} text='{10}'" -f $h, $par, $cls, $id, $vis, $en, $r.L, $r.T, $r.R, $r.B, $txt)
}

try {
  Add-Type -AssemblyName UIAutomationClient
  Add-Type -AssemblyName UIAutomationTypes
  $root = [System.Windows.Automation.AutomationElement]::RootElement
  $pidCond = New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ProcessIdProperty, [int]$proc.Id)
  $wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $pidCond)
  L ("uia_windows_for_pid=" + $wins.Count)
  foreach ($w in $wins) {
    $c = $w.Current
    L ("uia_window name='$($c.Name)' class='$($c.ClassName)'")
    $kids = $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    L ("uia_descendants=" + $kids.Count)
  }
  $walker = [System.Windows.Automation.TreeWalker]::RawViewWalker
  function Dump-Raw([System.Windows.Automation.AutomationElement]$el, [int]$depth, [int]$max) {
    if (-not $el -or $depth -gt $max) { return }
    $c = $el.Current
    $name = [string]$c.Name
    if ($name.Length -gt 80) { $name = $name.Substring(0, 80) }
    L (("{0}RAW {1} name='{2}' id='{3}' class='{4}' en={5}" -f ('  ' * $depth), $c.ControlType.ProgrammaticName, $name, $c.AutomationId, $c.ClassName, $c.IsEnabled))
    $ch = $walker.GetFirstChild($el)
    while ($ch) {
      Dump-Raw $ch ($depth + 1) $max
      $ch = $walker.GetNextSibling($ch)
    }
  }
  L '---- UIA RawView (depth 4) ----'
  foreach ($w in $wins) { Dump-Raw $w 0 4 }
} catch {
  L ("UIA error: " + $_.Exception.Message)
}

L '---- EnumChildWindows (main) ----'
$script:childBag = [System.Collections.Generic.List[IntPtr]]::new()
$enumChild = [PeDumpWin32+EnumProc] {
  param([IntPtr]$h, [IntPtr]$l)
  $script:childBag.Add($h)
  return $true
}
[void][PeDumpWin32]::EnumChildWindows($hwndMain, $enumChild, [IntPtr]::Zero)
L ("child_count=$($script:childBag.Count)")
foreach ($h in $script:childBag) {
  L ('  ' + (Fmt-Hwnd $h))
  $cls = [PeDumpWin32]::Cls($h)
  if ($cls -match 'Toolbar|ToolBar') {
    $n = [PeDumpWin32]::SendMessage($h, [PeDumpWin32]::TB_GETBUTTONCOUNT, [IntPtr]::Zero, [IntPtr]::Zero).ToInt32()
    L ("    TB_GETBUTTONCOUNT=$n  (lecture seule, pas de press)")
    if ($n -gt 0 -and $n -lt 80) {
      for ($i = 0; $i -lt $n; $i++) {
        $sb = New-Object System.Text.StringBuilder 256
        $len = [PeDumpWin32]::SendMessage($h, [PeDumpWin32]::TB_GETBUTTONTEXTW, [IntPtr]$i, $sb).ToInt32()
        L ("    btn[$i] len=$len text='$($sb.ToString())'")
      }
    }
  }
}

L '---- EnumWindows same pid ----'
$script:topBag = [System.Collections.Generic.List[IntPtr]]::new()
$pidWanted = [uint32]$proc.Id
$enumTop = [PeDumpWin32+EnumProc] {
  param([IntPtr]$h, [IntPtr]$l)
  $wpid = [uint32]0
  [void][PeDumpWin32]::GetWindowThreadProcessId($h, [ref]$wpid)
  if ($wpid -eq $pidWanted) { $script:topBag.Add($h) }
  return $true
}
[void][PeDumpWin32]::EnumWindows($enumTop, [IntPtr]::Zero)
L ("toplevel_same_pid=$($script:topBag.Count)")
foreach ($h in $script:topBag) {
  L ('  ' + (Fmt-Hwnd $h))
}

L '---- keywords ----'
foreach ($ln in @($lines.ToArray())) {
  if ($ln -match 'Clean|Check|Weak|Normal|Strong|Flash|OpenFiles') {
    L ("KW $ln")
  }
}

$lines | Set-Content -LiteralPath $out -Encoding UTF8
