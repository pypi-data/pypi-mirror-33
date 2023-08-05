==========================
MCU Definition Word List
==========================

``!=``
------
Compare two numbers on the stack.


``&``
-----
Bitwise AND of two numbers on the stack.


``*``
-----
Multiply two numbers on the stack.


``+``
-----
Add two numbers on the stack.


``-``
-----
Subtract two numbers on the stack.


``/``
-----
Divide two numbers on the stack.


``<``
-----
Compare two numbers on the stack.


``<<``
------
Bitwise shift left.


``<=``
------
Compare two numbers on the stack.


``==``
------
Compare two numbers on the stack.


``>``
-----
Compare two numbers on the stack.


``>=``
------
Compare two numbers on the stack.


``>>``
------
Bitwise shift right.


``AND``
-------
Logical AND of two numbers on the stack


``BASED-ON``
------------
Tell that a memory map definition builds on an other definition.
All the definitions are merged when used.
Example::

    based-on <name>


``DROP``
--------
Remove and forget about topmost element on the stack.


``DUP``
-------
Duplicate the topmost element on the stack.


``FLOAT``
---------
Convert TOS to a floating point number.


``IFTE``
--------
If then else for 3 values on the stack: predicate, value_true,
value_false.


``INT``
-------
Convert TOS to an integer.


``LIST``
--------
testing only: print all knwon words to stdout


``MAX``
-------
Leave the larger of two values on the stack.


``MEMORY-MAP-BEGIN``
--------------------
Start the definition of a memory map for a MCU. It's expected that the
NAME_ and SEGMENT_ commands are used to define a memory map.
Example::

    memory-map-begin
        name        LOGICAL
        # declare a "DATA" segment at the beginning of RAM
        segment     .data           in:RAM
        segment     .bss            in:RAM
        segment     .noinit         in:RAM
        symbol      _stack          in:RAM,location:end


        # declare multiple segments that are located in FLASH
        programmable segment     .text           in:FLASH
        programmable segment     .const          in:FLASH
        programmable segment     .data_init      in:FLASH,mirror:.data
    memory-map-end

    memory-map-begin
        name         MSP430F2xx
        based-on     LOGICAL
        read-only    segment     .bootloader     0x0c00-0x0fff
        programmable segment     .infomem        0x1000-0x10ff
        programmable segment     .infoD          0x1000-0x103f
        programmable segment     .infoC          0x1040-0x107f
        programmable segment     .infoB          0x1080-0x10bf
        programmable segment     .infoA          0x10c0-0x10ff
        programmable segment     .vectors        0xffe0-0xffff
    memory-map-end


``MEMORY-MAP-END``
------------------
Terminate current memory map definition. See `MEMORY-MAP-BEGIN`_.


``MIN``
-------
Leave the smaller of two values on the stack.


``NAME``
--------
Set the name of a memory map.
Example::

    name <name>


``NEG``
-------
Negate number on stack.


``NOT``
-------
Logical NOT of number on stack


``OR``
------
Logical OR of two numbers on the stack


``OVER``
--------
Push a copy of the second element on the stack.


``PICK``
--------
Push a copy of the N'th element on the stack.


``PROGRAMMABLE``
----------------
Set flag that the next defined segment is programmed on the target.
Example::

    programmable segment     .text           in:FLASH


``READ-ONLY``
-------------
Set flag that the next defined segment is read-only (not programmed to
target).
Example::

    read-only  segment bootloader 0x0c00-0x0fff


``SEGMENT``
-----------
Example::

    segment <name>  <memory_range>

Defines a segment.
Previously set flags are applied and cleared.
``<memory_range>`` can be an address range like ``0x0200-0x0300`` or a
set of ``key:value`` pairs:

``in:<segment_name>``
    This segment is placed within an other parent segment. The memory
    range is inherited from the parent. Multiple segments can be placed
    in one parent segment.

``mirror:<segment_name>``
    The contents of this segment will be a copy of the given one. A typical use is
    to make a copy of the ``.data`` section that is in RAM and needs to
    be initialized (by the startup code) from a copy located in Flash memory::

        programmable segment     .data_init      in:FLASH,mirror:.data


``SWAP``
--------
Exchange the two topmost elements on the stack.


``SYMBOL``
----------
Example::

    symbol <name> <address>

Defines a symbol with the value specified. ``<address>`` can also be a computed
value. e.g. ``in:RAM,location:end``.

Supported are: ``in:<segment_name>`` and ``location:[start|end]``.  These
values are computed at load time, i.e. the segment still have the address
range specified in the definition (opposed to the values after the linker has
"shrinked" the segments to the size of actually present data). Note that
``location:end`` is the segments last address plus one (end is exclusive in
this case).


``TEMPLATE-BEGIN``
------------------
Read and execute a template. This command consists of 3 sections:

- definition of a text
- definition of a set of variables
- values for the variables

template-begin
    Begin a template. What follows is the text of the template itself.  It may
    contain special words that will be used as variables.  They can have any
    name. The template text is finished with the command
    'template_variables'.

template-variables
    The names of the variables follow. These are the words that are used in the
    previously defined template text. This section is terminated by
    'template_values'.

template-values
    Values are following until 'template_end' is found. Each word that is read
    is assigned to the list of values. When the list of values has the same
    length as the list of variables are they replaced in the template text and
    the resulting text is parsed again.

template-end
    Denotes the end of a values section in a template.

Example::

    template-begin
        memory-map-begin
            name        <MCU>
            based-on    MSP430F2xx
                         segment     RAM             <RAM>
            programmable segment     FLASH           <FLASH>
        memory-map-end
    template-variables
        <MCU>           <RAM>           <FLASH>
    template-values
        MSP430F2001     0x0200-0x027f   0xfc00-0xffdf   # 128B RAM, 1kB Flash
        MSP430F2002     0x0200-0x027f   0xfc00-0xffdf   # 128B RAM, 1kB Flash
        MSP430F2003     0x0200-0x027f   0xfc00-0xffdf   # 128B RAM, 1kB Flash
        MSP430F2011     0x0200-0x027f   0xf800-0xffdf   # 128B RAM, 2kB Flash
        MSP430F2012     0x0200-0x027f   0xf800-0xffdf   # 128B RAM, 2kB Flash
        MSP430F2013     0x0200-0x027f   0xf800-0xffdf   # 128B RAM, 2kB Flash
    template-end


``^``
-----
Bitwise XOR of two numbers on the stack.


``|``
-----
Bitwise OR of two numbers on the stack.


``~``
-----
Bitwise invert of number on stack.

