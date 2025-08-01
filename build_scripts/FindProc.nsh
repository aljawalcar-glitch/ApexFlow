; FindProc.nsh
;
; Based on a script by Yaroslav Pidstryhach
; Trimmed down and modified by Amir Szekely
;
; Usage:
;   ${FindProc} "process.exe"
;
; Result is returned in $R0
;   $R0=0       Process not found
;   $R0!=0      Process found
;

!macro _FindProc _FILE
  System::Call 'kernel32::CreateToolhelp32Snapshot(i 2, i 0) i .r0'
  StrCmp $0 0 _FindProc_error

  System::Alloc 304
  pop $1

  System::Call 'kernel32::Process32First(i r0, i r1) i .r2'
  StrCmp $2 0 _FindProc_notfound

  _FindProc_loop:
    System::Call '*$1(i,i,i,i,i,i,i,i,i,i 260) i .r3'
    StrCmp $3 "${_FILE}" _FindProc_found

    System::Call 'kernel32::Process32Next(i r0, i r1) i .r2'
    StrCmp $2 0 _FindProc_notfound
    Goto _FindProc_loop

  _FindProc_found:
    System::Free $1
    System::Call 'kernel32::CloseHandle(i r0)'
    StrCpy $R0 1
    Goto _FindProc_done

  _FindProc_notfound:
    System::Free $1
    System::Call 'kernel32::CloseHandle(i r0)'
    StrCpy $R0 0
    Goto _FindProc_done

  _FindProc_error:
    System::Free $1
    StrCpy $R0 0

  _FindProc_done:
!macroend
!define FindProc '!insertmacro "_FindProc"'
