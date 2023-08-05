=================
 Forth Word List
=================
.. .. contents::

``!``
-----
Store word value. 

Stack: ``( n adr -- )``

Availability: target and host

Defined in file(s): ``_memory.forth:34`` and ``forth.py``

``!=``
------
Tests two numbers for unequality. 

Stack: ``( x y -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:268`` and ``forth.py``

``"``
-----
Put a string on the stack.


Availability: host

Defined in file(s): ``forth.py``

``'``
-----
Push reference to next word on stack.


Availability: host

Defined in file(s): ``forth.py``

``'"'``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:68``

``'('``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:66``

``')'``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:67``

``'-'``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:71``

``'.'``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:72``

``'0'``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:70``

``':'``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:56``

``';'``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:65``

``'A'``
-------


Availability: target and host

Defined in file(s): ``__init__.forth:69``

``'\N'``
--------
ASCII code for line feed. 

Availability: target and host

Defined in file(s): ``__init__.forth:26``

``(``
-----
Start a comment and read to its end (``)``).

There is a special comment ``( > text... )`` which is recognized by the
documentation tool. All these type of comments are collected and
assigned to the next declaration.


Availability: host

Defined in file(s): ``forth.py``

``*``
-----
Multiply two numbers on the stack.


Availability: host

Defined in file(s): ``forth.py``

``+``
-----
Add two 16 bit values. 

Stack: ``( n n -- n )``

Availability: target and host

Defined in file(s): ``_builtins.forth:105`` and ``forth.py``

``,``
-----
Append value from stack to current definition.


Availability: host

Defined in file(s): ``forth.py``

``-``
-----
Subtract two 16 bit values. 

Stack: ``( n n -- n )``

Availability: target and host

Defined in file(s): ``_builtins.forth:112`` and ``forth.py``

``-ROT``
--------
Rotate 3 items on the stack. 1st gets 3rd.


Availability: host

Defined in file(s): ``forth.py``

``.``
-----
Output element on stack.


Availability: host

Defined in file(s): ``forth.py``

``."``
------
Output a string.


Availability: host

Defined in file(s): ``forth.py``

``/``
-----
Divide two numbers on the stack.


Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``__init__.forth:15`` and ``forth.py``

``/MOD``
--------
Put quotient and reminder on stack.


Availability: host

Defined in file(s): ``forth.py``

``0=``
------
Test if number equals zero. 

Stack: ``( x -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:277`` and ``forth.py``

``0>``
------
Test if number is positive. 

Stack: ``( x -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:285`` and ``forth.py``

``1+``
------
Increment value on stack by one. 

Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``__init__.forth:19`` and ``_msp430_lowlevel.forth:101`` and ``forth.py``

``1-``
------
Decrement value on stack by one. 

Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``__init__.forth:20`` and ``_msp430_lowlevel.forth:120`` and ``forth.py``

``2*``
------
Multiply by two [arithmetic left shift]. 

Stack: ``( n -- n*2 )``

Availability: target and host

Defined in file(s): ``_builtins.forth:148`` and ``forth.py``

``2+``
------
Increment value on stack by two. 

Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``_msp430_lowlevel.forth:107`` and ``forth.py``

``2-``
------
Decrement value on stack by two. 

Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``_msp430_lowlevel.forth:126`` and ``forth.py``

``2/``
------
Divide by two [arithmetic right shift]. 

Stack: ``( n -- n/2 )``

Availability: target and host

Defined in file(s): ``_builtins.forth:154`` and ``forth.py``

``2DROP``
---------
Drop two items from the stack. 

Stack: ``( n n -- )``

Availability: target and host

Defined in file(s): ``__init__.forth:9`` and ``_msp430_lowlevel.forth:138``

``2DUP``
--------


Stack: ``( y x -- y x y x )``

Availability: target and host

Defined in file(s): ``__init__.forth:10``

``4+``
------
Increment value on stack by four. 

Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``__init__.forth:21`` and ``_msp430_lowlevel.forth:113`` and ``forth.py``

``4-``
------
Decrement value on stack by four. 

Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``__init__.forth:22`` and ``_msp430_lowlevel.forth:132`` and ``forth.py``

``:``
-----
Begin defining a function. Example: ``: ADD-ONE 1 + ;``


Availability: host

Defined in file(s): ``forth.py``

``;``
-----
End definition of function. See `:`_


Availability: host

Defined in file(s): ``forth.py``

``<``
-----
Compare two numbers. 

Stack: ``( x y -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:219`` and ``forth.py``

``<=``
------
Compare two numbers. 

Stack: ``( x y -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:235`` and ``forth.py``

``=``
-----
Tests two numbers for equality. 

Stack: ``( x y -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:260`` and ``forth.py``

``==``
------
Tests two numbers for equality. 

Stack: ``( x y -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:251`` and ``forth.py``

``>``
-----
Compare two numbers. 

Stack: ``( x y -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:227`` and ``forth.py``

``>=``
------
Compare two numbers. 

Stack: ``( x y -- b )``

Availability: target and host

Defined in file(s): ``_builtins.forth:243`` and ``forth.py``

``>R``
------
Move x to the return stack. 

Stack: ``( x -- )``

Availability: target

Defined in file(s): ``_builtins.forth:83``

``?``
-----
? Fetches the integer at an address and prints it. 

Stack: ``( addr -- )``

Availability: target and host

Defined in file(s): ``__init__.forth:212``

``?DUP``
--------
DUP top of stack but only if not zero.


Availability: host

Defined in file(s): ``forth.py``

``@``
-----
Fetch word value. 

Stack: ``( adr -- n )``

Availability: target and host

Defined in file(s): ``_memory.forth:27`` and ``forth.py``

``@!``
------
Move word from memory to memory, 16 bit. 

Stack: ``( src-adr dst-adr -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:181``

``ABORT``
---------
Terminate program and restart from the beginning.
The implementation is is also providing the 'main' entry point. 

Availability: target

Defined in file(s): ``core.forth:15``

``AGAIN``
---------
BEGIN loop-part AGAIN 

Availability: target and host

Defined in file(s): ``__init__.forth:151``

``ALLOT``
---------
Allocate memory in RAM or ROM.


Availability: host

Defined in file(s): ``forth.py``

``AND``
-------
Bitwise AND. 

Stack: ``( n n -- n )``

Availability: target and host

Defined in file(s): ``_builtins.forth:120`` and ``forth.py``

``ASM-CALL``
------------
Helper to write a call in assembler. 
Example::

   CODE PUTCHAR ( u -- 
       ASM-TOS->R15
       ASM-CALL putchar
       ASM-NEXT
   END-CODE 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:60``

``ASM-DROP``
------------
Emit assembler for DROP. 
Example::

   CODE DROP-DEMO ( n -- 
       ASM-DROP
       ASM-NEXT
   END-CODE 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:32``

``ASM-NEXT``
------------
Emit assembler for NEXT. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:23``

``ASM-R15->TOS``
----------------
Emit assembler to push R15 on stack. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:41``

``ASM-TOS->R14``
----------------
Emit assembler to pop top of stack to register R14. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:38``

``ASM-TOS->R15``
----------------
Emit assembler to pop top of stack to register R15. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:35``

``ASM-TOS->W``
--------------
Emit assembler to pop top of stack to register W. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:44``

``ASM-W->TOS``
--------------
Emit assembler to push register W on stack. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:47``

``BEGIN``
---------
Example: ``BEGIN loop-part condition UNTIL`` 

Availability: target and host

Defined in file(s): ``__init__.forth:136``

``BL``
------
BL [BLank] is a standard FORTH word for space. 

Availability: target and host

Defined in file(s): ``__init__.forth:28``

``BRANCH``
----------
Relative jump within a thread. 

Availability: target and host

Defined in file(s): ``_builtins.forth:22`` and ``forth.py``

``BRANCH0``
-----------
Realtive jump within a thread. But only jump if value on stack is false. 

Availability: target and host

Defined in file(s): ``_builtins.forth:28`` and ``forth.py``

``BS``
------
Emit the backspace character. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:11``

``C!``
------
Store byte value. 

Stack: ``( n adr -- )``

Availability: target

Defined in file(s): ``_memory.forth:19``

``C@``
------
Fetch byte value. 

Stack: ``( adr -- n )``

Availability: target

Defined in file(s): ``_memory.forth:11``

``C@!``
-------
Move byte from memory to memory, 8 bit. 

Stack: ``( src-adr dst-adr -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:173``

``CASE``
--------
::

              (some value on the stack
              CASE
              test1 OF ... ENDOF
              test2 OF ... ENDOF
              testn OF ... ENDOF
              ... (default case
              ENDCASE

Availability: target and host

Defined in file(s): ``__init__.forth:299``

``CHAR``
--------
Push ASCII code of next character.


Availability: host

Defined in file(s): ``forth.py``

``CODE``
--------
Begin defining a native code function. CODE words are executed on the
host to get cross compiled. Therefore they have to output assembler
code for the target. Example::

    ( > Increment value on stack by one. )
    CODE 1+ ( n -- n )
        ." \t inc 0(SP) \n "
        ASM-NEXT
    END-CODE

There is a number of supporting functions for outputting assembler.
E.g. `ASM-NEXT`_, `ASM-DROP`_, `ASM-TOS->R15`_, `ASM-R15->TOS`_,
`ASM-TOS->W`_, `ASM-W->TOS`_

Note that the NEXT instruction is not automatically inserted and must be
added manually (see `ASM-NEXT`_ in example above).


Availability: host

Defined in file(s): ``forth.py``

``CONSTANT``
------------
Declare a constant. Assign next word to value from stack.
Example: ``0 CONSTANT NULL``


Availability: host

Defined in file(s): ``forth.py``

``CR``
------
CR prints a carriage return. 

Availability: target and host

Defined in file(s): ``__init__.forth:31``

``CREATE``
----------
Create a frame, typically used for variables.


Availability: host

Defined in file(s): ``forth.py``

``CRESET``
----------
Bit clear operation, 8 bit. 
Example: ``BIT0 P1OUT CRESET`` 

Stack: ``( n adr -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:17``

``CROSS-COMPILE``
-----------------
Output cross compiled version of function. Example:: ``CROSS-COMPILE DROP``


Availability: host

Defined in file(s): ``forth.py``

``CROSS-COMPILE-CORE``
----------------------
Generate init code for forth runtime and core words. 

Availability: target and host

Defined in file(s): ``core.forth:47``

``CROSS-COMPILE-MISSING``
-------------------------
Compile all the words that are used by other compiled words but are not
yet translated. While compiling words, new words can be found which are
then also compiled.


Availability: host

Defined in file(s): ``forth.py``

``CROSS-COMPILE-VARIABLES``
---------------------------
Output section with variables (values in RAM).
        


Availability: host

Defined in file(s): ``forth.py``

``CSET``
--------
Bit set operation, 8 bit. 
Example: ``BIT0 P1OUT CSET`` 

Stack: ``( n adr -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:26``

``CTESTBIT``
------------
Bit test operation, 8 bit. 
Example: ``BIT0 P1IN CTESTBIT IF 1 THEN 0 ENDIF`` 

Stack: ``( mask adr -- bool )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:44``

``CTOGGLE``
-----------
Bit toggle operation, 8 bit. 
Example: ``BIT0 P1OUT CTOGGLE`` 

Stack: ``( n adr -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:35``

``DEFINE``
----------
Emit the text for a define. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:20``

``DELAY``
---------
Simple busy-wait type delay. 3 cycles/loop. 
Example: ``20 DELAY`` 

Stack: ``( n -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:149``

``DEPENDS-ON``
--------------
Mark word as used so that it is included in cross compilation. Useful
when using other words within CODE_ definitions.


Availability: host

Defined in file(s): ``forth.py``

``DINT``
--------
Disable interrupts. 

Stack: ``( -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:202``

``DO-INTERRUPT``
----------------
Entering an interrupt handler. For internal use only. 

Availability: target

Defined in file(s): ``_interrupts.forth:36``

``DOCOL``
---------
Internal helper to execute a thread of forth instructions. 

Availability: target

Defined in file(s): ``core.forth:24``

``DROP``
--------
Remove value from top of stack. 

Stack: ``( x -- )``

Availability: target and host

Defined in file(s): ``_builtins.forth:42`` and ``forth.py``

``DUP``
-------
Duplicate value on top of stack. 

Stack: ``( x -- x x )``

Availability: target and host

Defined in file(s): ``_builtins.forth:48`` and ``forth.py``

``EINT``
--------
Enable interrupts. 

Stack: ``( -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:196``

``ELSE``
--------
See IF_. 

Availability: target and host

Defined in file(s): ``__init__.forth:121``

``EMIT``
--------
Output number on stack as Unicode character.


Availability: host

Defined in file(s): ``forth.py``

``END-CODE``
------------
End definition of a native code function. See CODE_.


Availability: host

Defined in file(s): ``forth.py``

``END-INTERRUPT``
-----------------
End definition of a native code function. See INTERRUPT_ for example.


Availability: host

Defined in file(s): ``forth.py``

``ENDCASE``
-----------
See CASE_. 

Availability: target and host

Defined in file(s): ``__init__.forth:317``

``ENDIF``
---------
Alias for THEN_, See IF_. 

Availability: target and host

Defined in file(s): ``__init__.forth:114``

``ENDOF``
---------
See CASE_. 

Availability: target and host

Defined in file(s): ``__init__.forth:312``

``ENTER-LPM0``
--------------
Enter low-power mode LPM0. 

Stack: ``( n -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:208``

``ENTER-LPM1``
--------------
Enter low-power mode LPM1. 

Stack: ``( n -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:214``

``ENTER-LPM2``
--------------
Enter low-power mode LMP2. 

Stack: ``( n -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:220``

``ENTER-LPM3``
--------------
Enter low-power mode LPM3. 

Stack: ``( n -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:226``

``ENTER-LPM4``
--------------
Enter low-power mode LPM4. 

Stack: ``( n -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:232``

``EXIT``
--------
a.k.a return from subroutine. 

Availability: target

Defined in file(s): ``core.forth:34``

``EXIT-INTERRUPT``
------------------
Restore state at exit of interrupt handler. For internal use only. 

Stack: ``( R: int-sys -- )``

Availability: target

Defined in file(s): ``_interrupts.forth:52``

``HASH``
--------
Emit the hash character. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:17``

``HEADER``
----------
Generate a header in the assembler file 

Stack: ``( str -- )``

Availability: target and host

Defined in file(s): ``_helpers.forth:16``

``HERE``
--------
Put position [within frame] on stack


Availability: host

Defined in file(s): ``forth.py``

``IF``
------
Examples:

- ``condition IF true-part THEN rest`` 
- ``condition IF true-part ELSE false-part THEN`` 
- ``condition IF true-part ELSE false-part ENDIF`` 

Availability: target and host

Defined in file(s): ``__init__.forth:100``

``IMMEDIATE``
-------------
Tag current function definition as immediate. This means that it is
executed even during compilation.


Availability: host

Defined in file(s): ``forth.py``

``INCLUDE``
-----------
Include and execute definitions from an other file. Example:
``INCLUDE helper.forth``


Availability: host

Defined in file(s): ``forth.py``

``INTERRUPT``
-------------
Begin defining an interrupt function. Example::

    PORT1_VECTOR INTERRUPT handler_name
        WAKEUP
        0 P1IFG C!
    END-INTERRUPT

Words defined with ``INTERRUPT`` must not be called from user code.


Availability: host

Defined in file(s): ``forth.py``

``INVERT``
----------
Bitwise invert. 

Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``_builtins.forth:141`` and ``forth.py``

``LF``
------
Emit the line feed character. 

Availability: target and host

Defined in file(s): ``_asm_snippets.forth:14``

``LINE``
--------
Generate a simple line for headers 

Stack: ``( -- )``

Availability: target and host

Defined in file(s): ``_helpers.forth:11``

``LIT``
-------
Put a literal [next element within thread] on the stack. 

Availability: target and host

Defined in file(s): ``_builtins.forth:16`` and ``forth.py``

``LITERAL``
-----------


Availability: target and host

Defined in file(s): ``__init__.forth:45``

``LSHIFT``
----------
Logical left shift by u bits. 

Stack: ``( n u -- n*2^u )``

Availability: target and host

Defined in file(s): ``_builtins.forth:161`` and ``forth.py``

``MOD``
-------


Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``__init__.forth:16``

``NEGATE``
----------
NEGATE leaves the negative of a number on the stack. 

Availability: target and host

Defined in file(s): ``__init__.forth:37``

``NIP``
-------


Stack: ``( x y -- y )``

Availability: target and host

Defined in file(s): ``__init__.forth:194``

``NOP``
-------
NOP - waste some small amount of CPU time. 

Stack: ``( -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:190``

``NOT``
-------
Boolean invert. 

Stack: ``( b -- b )``

Availability: target and host

Defined in file(s): ``__init__.forth:42`` and ``_builtins.forth:185`` and ``forth.py``

``OF``
------
See CASE_. 

Availability: target and host

Defined in file(s): ``__init__.forth:304``

``OR``
------
Bitwise OR. 

Stack: ``( n n -- n )``

Availability: target and host

Defined in file(s): ``_builtins.forth:127`` and ``forth.py``

``OVER``
--------
Push a copy of the second element on the stack. 

Stack: ``( y x -- y x y )``

Availability: target and host

Defined in file(s): ``_builtins.forth:56`` and ``forth.py``

``PICK``
--------
Push a copy of the N'th element. 

Stack: ``( n -- n )``

Availability: target and host

Defined in file(s): ``_builtins.forth:64`` and ``forth.py``

``R>``
------
Move x from the return stack to the data stack. 

Stack: ``( -- x )``

Availability: target

Defined in file(s): ``_builtins.forth:90``

``R@``
------
Copy x from the return stack to the data stack. 

Stack: ``( -- x )``

Availability: target

Defined in file(s): ``_builtins.forth:96``

``RAM``
-------
Select RAM as target for following CREATE_ calls.


Availability: host

Defined in file(s): ``forth.py``

``RECURSE``
-----------
Call currently defined word. This is used to write recursive functions.
        


Availability: host

Defined in file(s): ``forth.py``

``REPEAT``
----------
See WHILE_. 

Availability: target and host

Defined in file(s): ``__init__.forth:169``

``RESET``
---------
Bit clear operation, 16 bit. 
Example: ``CCIE TA0CCTL1 RESET`` 

Stack: ``( n adr -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:61``

``ROM``
-------
Select ROM/Flash as target for following CREATE_ calls.


Availability: host

Defined in file(s): ``forth.py``

``ROT``
-------
Rotate 3 items on the stack. 3rd gets 1st.


Availability: host

Defined in file(s): ``forth.py``

``RSHIFT``
----------
Logical right shift by u bits. 

Stack: ``( n u -- n/2^u )``

Availability: target and host

Defined in file(s): ``_builtins.forth:171`` and ``forth.py``

``SET``
-------
Bit set operation, 16 bit. 
Example: ``CCIE TA0CCTL1 SET`` 

Stack: ``( n adr -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:69``

``SHOW``
--------
Show internals of given word. Used to debug.


Availability: host

Defined in file(s): ``forth.py``

``SIGN-EXTEND``
---------------
Sign extend an 8 bit value on stack to 16 bits. 

Stack: ``( n -- n )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:167``

``SPACE``
---------
SPACE prints a space. 

Availability: target and host

Defined in file(s): ``__init__.forth:34``

``SPACES``
----------
Write given number of spaces. Example:: ``20 SPACES``.

Stack: ``( n -- )``

Availability: target and host

Defined in file(s): ``__init__.forth:199``

``SWAP``
--------
Exchange the two topmost values on the stack. 

Stack: ``( y x -- x y )``

Availability: target and host

Defined in file(s): ``_builtins.forth:73`` and ``forth.py``

``SWPB``
--------
Swap high/low byte. 

Stack: ``( n -- n )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:161``

``TESTBIT``
-----------
Bit test operation, 16 bit. 
Example: ``CCIFG TA0CCTL1 TESTBIT IF 1 ELSE 0 ENDIF`` 

Stack: ``( mask adr -- bool )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:85``

``THEN``
--------
See IF_. 

Availability: target and host

Defined in file(s): ``__init__.forth:107``

``TO``
------
Write to a VALUE_. Example: ``123 SOMEVALUE TO``


Availability: host

Defined in file(s): ``forth.py``

``TOGGLE``
----------
Bit toggle operation, 16 bit. 
Example: ``CCIE TA0CCTL1 TOGGLE`` 

Stack: ``( n adr -- )``

Availability: target

Defined in file(s): ``_msp430_lowlevel.forth:77``

``TUCK``
--------


Stack: ``( x y -- y x y )``

Availability: target and host

Defined in file(s): ``__init__.forth:195``

``UNLESS``
----------
UNLESS is the same as IF_ but the test is reversed. 

Availability: target and host

Defined in file(s): ``__init__.forth:187``

``UNTIL``
---------
See BEGIN_. 

Availability: target and host

Defined in file(s): ``__init__.forth:141``

``VALUE``
---------
Allocate a variable. Creates space in RAM and a value getter
function.

Example::

    0 VALUE X
    X       \ -> puts 0 on stack
    5 X TO
    X       \ -> puts 5 on stack


Availability: host

Defined in file(s): ``forth.py``

``VARIABLE``
------------
Allocate a variable. Creates space in RAM and an address getter
function.


Availability: host

Defined in file(s): ``forth.py``

``WAKEUP``
----------
Patch the saved status register so that LPM modes are exit after the
interrupt handler is finished.

Only allowed directly in INTERRUPT_ definition. Not in called functions.

May be called multiple times. 

Stack: ``( R: int-sys -- int-sys )``

Availability: target

Defined in file(s): ``_interrupts.forth:75``

``WHILE``
---------
Example: ``BEGIN condition WHILE loop-part REPEAT`` 

Availability: target and host

Defined in file(s): ``__init__.forth:162``

``WITHIN``
----------
``c a b WITHIN`` returns true if a <= c and c < b 
or define without ifs: ``OVER - >R - R>  U<``  

Availability: target and host

Defined in file(s): ``__init__.forth:216``

``WORD``
--------
Read next word from the source and put it on the stack.


Availability: host

Defined in file(s): ``forth.py``

``XOR``
-------
Bitwise XOR. 

Stack: ``( n n -- n )``

Availability: target and host

Defined in file(s): ``_builtins.forth:134`` and ``forth.py``

``ZERO``
--------
Erase memory area. 

Stack: ``( adr u -- )``

Availability: target

Defined in file(s): ``_builtins.forth:296``

``[``
-----
Change to interpretation mode.


Availability: host

Defined in file(s): ``forth.py``

``[']``
-------
Compile LIT_. 

Availability: target and host

Defined in file(s): ``__init__.forth:330``

``[CHAR]``
----------
Compile ASCII code of next character.


Availability: host

Defined in file(s): ``forth.py``

``[COMPILE]``
-------------
Get next word, look it up and add it to the current frame (not
executing immediate functions).


Availability: host

Defined in file(s): ``forth.py``

``\``
-----
Start a line comment and read to its end.


Availability: host

Defined in file(s): ``forth.py``

``]``
-----
Change to compilation mode.


Availability: host

Defined in file(s): ``forth.py``

``__COMPARE_HELPER``
--------------------
Internal helper. Providing several labels to be called from assembler:

- ``__set_true``    stack: ``x -- true`` 
- ``__set_false``   stack: ``x -- false`` 
- ``__drop_and_set_true``  stack: ``x y -- true`` 
- ``__drop_and_set_false`` stack: ``x y -- false`` 

Availability: target

Defined in file(s): ``_builtins.forth:203``

``__WRITE_TEXT``
----------------
internal helper for ``."`` 

Stack: ``( -- )``

Availability: target

Defined in file(s): ``_builtins.forth:308``
