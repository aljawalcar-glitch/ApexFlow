; KillProc.nsh
;
; Based on a script by Yaroslav Pidstryhach
; Trimmed down and modified by Amir Szekely
;
; Usage:
;   ${KillProc} "process.exe"
;

!macro _KillProc _proc
  System::Call 'kernel32::CreateToolhelp32Snapshot(i 2, i 0) i .r0'
  StrCmp $0 0 _KillProc_error

  System::Alloc 304
  pop $1

  System::Call 'kernel32::Process32First(i r0, i r1) i .r2'
  StrCmp $2 0 _KillProc_loop_end

  _KillProc_loop:
    System::Call '*$1(i,i,i,i,i,i,i,i,i,i 260) i .r3'
    StrCmp $3 "${_proc}" 0 _KillProc_next

    System::Call '*$1(i) i .r4' ; get the process ID
    System::Call 'kernel32::OpenProcess(i 1, i 0, i r4) i .r5'
    StrCmp $5 0 _KillProc_next
    System::Call 'kernel32::TerminateProcess(i r5, i 0)'
    System::Call 'kernel32::CloseHandle(i r5)'

  _KillProc_next:
    System::Call 'kernel32::Process32Next(i r0, i r1) i .r2'
    StrCmp $2 0 _KillProc_loop_end
    Goto _KillProc_loop

  _KillProc_loop_end:
    System::Free $1
    System::Call 'kernel32::CloseHandle(i r0)'
    Goto _KillProc_done

  _KillProc_error:
    System::Free $1

  _KillProc_done:
!macroend
!define KillProc '!insertmacro "_KillProc"'
