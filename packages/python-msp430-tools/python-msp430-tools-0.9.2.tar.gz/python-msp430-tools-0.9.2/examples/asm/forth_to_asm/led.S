;============================================================================
; LED example
;============================================================================
;============================================================================
; Core
;============================================================================
; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#include <msp430g2231.h>

; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Assign registers. 
#define RTOS R4 
#define IP R5 
#define W R6 

; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
; Memory for the return stack. 
.bss 
return_stack: .skip 2*16 
.return_stack_end: 

; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
.text
; Initial thread that is run. Hardcoded init-main-loop. 
thread: 
	 .word _INIT 
	 .word _MAIN 
	 .word _ABORT 

.text
.even
;----------------------------------------------------------------------------
; compilation of word GREEN_OFF
;----------------------------------------------------------------------------
_GREEN_OFF:
	br #_DOCOL
	.word _LIT, 64     ; 0x0040
	.word _LIT, 33     ; 0x0021
	.word _CRESET
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word GREEN_ON
;----------------------------------------------------------------------------
_GREEN_ON:
	br #_DOCOL
	.word _LIT, 64     ; 0x0040
	.word _LIT, 33     ; 0x0021
	.word _CSET
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word INIT
;----------------------------------------------------------------------------
_INIT:
	br #_DOCOL
	.word _LIT, 0      ; 0x0000
	.word _LIT, 33     ; 0x0021
	.word _C_store_
	.word _LIT, 65     ; 0x0041
	.word _LIT, 34     ; 0x0022
	.word _C_store_
	.word _LIT, 23168  ; 0x5a80
	.word _LIT, 288    ; 0x0120
	.word __store_
	.word _LIT, 4350   ; 0x10fe
	.word _LIT, 86     ; 0x0056
	.word _C_fetch__store_
	.word _LIT, 4351   ; 0x10ff
	.word _LIT, 87     ; 0x0057
	.word _C_fetch__store_
	.word _GREEN_ON
	.word _VERY_dash_LONG_dash_DELAY
	.word _GREEN_OFF
	.word _VERY_dash_LONG_dash_DELAY
	.word _VERY_dash_LONG_dash_DELAY
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word LONG-DELAY
;----------------------------------------------------------------------------
_LONG_dash_DELAY:
	br #_DOCOL
	.word _LIT, 65535  ; 0xffff
	.word _DELAY
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word MAIN
;----------------------------------------------------------------------------
_MAIN:
	br #_DOCOL
	.word _S2
	.word _BRANCH0, 14
	.word _GREEN_ON
	.word _SHORT_dash_DELAY
	.word _GREEN_OFF
	.word _SHORT_dash_DELAY
	.word _BRANCH, 10
	.word _RED_ON
	.word _LONG_dash_DELAY
	.word _RED_OFF
	.word _LONG_dash_DELAY
	.word _BRANCH, -28
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word RED_OFF
;----------------------------------------------------------------------------
_RED_OFF:
	br #_DOCOL
	.word _LIT, 1      ; 0x0001
	.word _LIT, 33     ; 0x0021
	.word _CRESET
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word RED_ON
;----------------------------------------------------------------------------
_RED_ON:
	br #_DOCOL
	.word _LIT, 1      ; 0x0001
	.word _LIT, 33     ; 0x0021
	.word _CSET
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word S2
;----------------------------------------------------------------------------
_S2:
	br #_DOCOL
	.word _LIT, 8      ; 0x0008
	.word _LIT, 32     ; 0x0020
	.word _CTESTBIT
	.word __NOT_
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word SHORT-DELAY
;----------------------------------------------------------------------------
_SHORT_dash_DELAY:
	br #_DOCOL
	.word _LIT, 20479  ; 0x4fff
	.word _DELAY
	.word _EXIT

.text
.even
;----------------------------------------------------------------------------
; compilation of word VERY-LONG-DELAY
;----------------------------------------------------------------------------
_VERY_dash_LONG_dash_DELAY:
	br #_DOCOL
	.word _LONG_dash_DELAY
	.word _LONG_dash_DELAY
	.word _EXIT

; ===========================================================================
; == __VARIABLES__
; ===========================================================================
.bss
; ===========================================================================
; == _builtins.forth
; ===========================================================================
.text
.even
;----------------------------------------------------------------------------
; compilation of native word BRANCH
;----------------------------------------------------------------------------
_BRANCH:
	 add @IP, IP 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word BRANCH0
;----------------------------------------------------------------------------
_BRANCH0:
	 mov @IP+, W 	; get offset 
	 tst 0(SP) 	; check TOS 
	 jnz .Lnjmp 	; do not adjust IP if non zero 
	 decd IP 	; offset is relative to position of offset, correct 
	 add W, IP 	; adjust IP 
.Lnjmp:	 incd SP 	; DROP 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word LIT
;----------------------------------------------------------------------------
_LIT:
	 push @IP+ 	; copy value from thread to stack 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word NOT
;----------------------------------------------------------------------------
__NOT_:
	 tst 0(SP)
	 jz __set_true
	 jmp __set_false

.text
.even
;----------------------------------------------------------------------------
; compilation of native word __COMPARE_HELPER
;----------------------------------------------------------------------------
___COMPARE_HELPER:
__drop_and_set_true:
	 incd SP 	; DROP 
__set_true:
	 mov # -1, 0(SP)
	 br @IP+ 	; NEXT 
__drop_and_set_false:
	 incd SP 	; DROP 
__set_false:
	 mov # 0, 0(SP)
	 br @IP+ 	; NEXT 

; ===========================================================================
; == _memory.forth
; ===========================================================================
.text
.even
;----------------------------------------------------------------------------
; compilation of native word !
;----------------------------------------------------------------------------
__store_:
	 pop W 
	 mov @SP+, 0(W) 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word C!
;----------------------------------------------------------------------------
_C_store_:
	 pop R15 
	 pop R14 
	 mov.b R14, 0(R15) 
	 br @IP+ 	; NEXT 

; ===========================================================================
; == _msp430_lowlevel.forth
; ===========================================================================
.text
.even
;----------------------------------------------------------------------------
; compilation of native word C@!
;----------------------------------------------------------------------------
_C_fetch__store_:
	 pop R15 
	 pop R14 
	 mov.b @R14, 0(R15) 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word CRESET
;----------------------------------------------------------------------------
_CRESET:
	 pop R15 
	 pop R14 
	 bic.b R14, 0(R15) 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word CSET
;----------------------------------------------------------------------------
_CSET:
	 pop R15 
	 pop R14 
	 bis.b R14, 0(R15) 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word CTESTBIT
;----------------------------------------------------------------------------
_CTESTBIT:
	 pop W 
	 bit.b @W, 0(SP) 
	 jz .cbit0 
	 mov # -1, 0(SP) 
	 jmp .cbit2 
.cbit0:
	 mov # 0, 0(SP) 
.cbit2:
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word DELAY
;----------------------------------------------------------------------------
_DELAY:
	 pop W 
.loop: 	 dec W 
	 jnz .loop 
	 br @IP+ 	; NEXT 

; ===========================================================================
; == core.forth
; ===========================================================================
.text
.even
;----------------------------------------------------------------------------
; compilation of native word ABORT
;----------------------------------------------------------------------------
_ABORT:
main: 	; also the main entry point.
	 mov # _stack, SP 
	 mov # .return_stack_end, RTOS 
	 mov # thread, IP 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word DOCOL
;----------------------------------------------------------------------------
_DOCOL:
	 decd RTOS 	; prepare to push on return stack 
	 mov IP, 0(RTOS) 	; save IP on return stack 
	 mov -2(IP), IP 	; get where we are now 
	 add # 4, IP 	; jump over 'br HASH DOCOL' 
	 br @IP+ 	; NEXT 

.text
.even
;----------------------------------------------------------------------------
; compilation of native word EXIT
;----------------------------------------------------------------------------
_EXIT:
	 mov @RTOS+, IP 	; get last position from return stack 
	 br @IP+ 	; NEXT 

;============================================================================
; Application
;============================================================================
