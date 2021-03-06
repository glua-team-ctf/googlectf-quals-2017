## Johnny Boy

This looks retro but somewhat futuristic! I always lose though, can you win? My friends solved this without IDA!
[![Youtube](https://img.youtube.com/vi/Dem8Fq6hkAw/0.jpg)](https://www.youtube.com/watch?v=Dem8Fq6hkAw)

##
The chall.ino.hex is a intel hex file used by avrdude (or other AVR programmers) to flash an Atmel AVR microcontroller.
In the video we can see someone playing a game on their Arduboy which is a Atmel ATmega 32u4 based 'gameboy'

So after digging around to remember how to convert the intel hex files to binary we come up with `objcopy -I ihex chall.ino.hex -O binary chall.bin`
Now that we have the hex converted to a raw binary we can dig through it to look for interesting bits.

First we ran `strings` on it and saw that we do have some of the strings displayed on screen in the binary. 'Press a button to start!' ect.
But no CTF{} string, so the flag must be stored as some sort of raw 'pixel data' that draws on the display.

If you run `hexdump -v -C` on the binary you can see the top of the file has some chunks of 'text like' data in between a bunch of NULLs.
Now lets use `xxd` and `tr` to re-structure the data and see if we can get something visual. `xxd -b -c 16 chall.bin | tr '0' ' '`

Using `xxd` in binary mode with a 16 column width and replacing all 0's with spaces shows our flag. It took some tinkering around with the xxd width before it displayed neatly.

```
   32 :                                                                                                                                                  ................
     33 :                                                                11          1111           11     1 1                                             ................
     34 :                       1111                                     11            11           11                               11                    ................
     35 :                      11 11   111 11  11   11  1111 11 1 111  1 1111111  11   11    111  1 1111 111 1   111  11 11    1111  11                    ...;c{...9......
     36 :                      11     11 11 1 1 11 11  11  111  111 11   11   11  11   11   11 11   11     1 1  11 11  11 11 1 11    11                    ...m.....l..m...
     37 :                      11     11 11 1 1 11 11  11  11     1111   11   11  11   11    1111   11     1 1  11 11  11 11   1111  11                    ...m..<..<..l...
     38 :                      11 11  11 11 1 1 11 11  11  11    11 11   11 1 11  11   11   11 11   11 11  1 1  11 11  11 11     111                       ...m..l..l..l8..
     39 :                       111    111  1 1 11  11 11 1111   111111   111  11 11111111 1111111   111 111 111 111   11 11 1 1111  11                    ...9..~s..w.m...
     3a :                                              11                                                                                                  ................
     3b :                                          111 1                                                                                                   ................
     3c :                                                                                                                                                  ................
     3d :                                                                                                                                                  ................
     3e :                                                                                                                                                  ................
     3f :                                                                                                                                                  ................
     4  :                                                                                                                                                  ................
     41 :                                                                                                                                                  ................
     42 :                                         111                     111 111 1                        1 1                                             .......w........
     43 :                                  11 1111 11                    11     1 1                                                                        ................
     44 :                                  1  11 1 111 1   111         1 1111   1 1   111    11 11       111 1   1111                                      .........6......
     45 :                                     11   11  11 11 11          11     1 1  11 11  11 11          1 1  111     11                                 .........l.. ...
     46 :                                     11   11  11 11111          11     1 1   1111  11 11          1 1   1111                                      .........l......
     47 :                                     11   11  11 11             11     1 1  11 11  11 11          1 1     11 1                                    .........l......
     48 :                                   1 111  11  11  1111        1 1111 111 11111111 1 1111        111 11111111   11                                 ............ ...
     49 :                                                                                      11                                                          ................
     4a :                                                                                   1111                                                           .........x......
     4b :                                                                                                                                                  ................
     4c :                                                                                                                                                  ................
     4d :                                                                                                                                                  ................
     4e :                                                                                                                                                  ................
     4f :                                                                                                                                                  ................
     5  :                                                                                                                                                  ................
     51 :                                              11         111 11 1                                       111                      111      111     ......;.......88
     52 :             11        1111 11111111 1111   1 1   1111  11 11 1 1                              1111 1  11 11                      11     11 11    ......m........l
     53 :              11      11 11 1 11 1 1 1      1 1    11   11 11 1 111 11 1 1 11 11  111 111       11  11    11 11111    111 1111 1  1111      11 1  ......m.........
     54 : 1 111 11 11  11      11      11   1 111   11      11   11 11 1 1 11 11  11 11 11  11 11        11  11  111   11111 1 1 11 111 11 11 11   111     ...1..m..l..}..8
     55 : 111 1111      11     11      11   1 1      1 1 11 11   11 11 1 1 11 11  11 11 11  11 11        111 1     11  1 1 1 1 1111 1 1  1 11 11     11    ...1..m..l..U.[.
     56 : 11    11 11  11      11 11   11   1 1      1 1 11 11   11 11 1 1 11 11  11 11 11   1 1         11  11 11 11  1 1 1 1 1    1 1  1 11 11  11 11    ...1..m..(..U.[l
     57 : 11       111 11       111   1111 11 11     1 1  111     111  1 1 11 11  11 11 11   111        1111  11 111   1 1 1   1111 1 1  111111    111  1  ...{..9..8.nT.~9
     58 : 111  111 11  11                              11                                    11                                                            ......... ......
     59 :             11                                                                   111    1 11111                                                  ................
     5a :                                                                                                                                    
     ```

