Communication Protocols
1
DTI-1 has an isolated serial port, the RS485.
DTI-1 can support more than 4 different communication protocols by the same time; include 
MODBUS-ASCII, ASCII-RTU, Meter-BUS, the Fuji Extended Protocol and more than 10 compatible 
communication protocols used by Huizhongs flow meters.
MODBUS is a very commonly used industrial protocol. Both the RTU and the ASCII format of MODBUS is
supported
The Fuji Extended Protocol is developed based on the protocol used in a Japanese ultrasonic flow meter. It
is totally compatible with that of Version 7 flow meter.
DTI-1 can be used as a sample RTU terminal. The 4-20mA output in the DTI-1 can be used to open an 
analog proportional valve; The OCT output can be used to control the turn-on and turn-off of other devices 
such as a pump. The analog input can be used to input pressure or temperatures signals.
There is a programmable device address (or ID number) located at window M46. When DTI-1 is used in a 
network, all the parameters of the flow meter can be programmed through the network, except the device 
address that needs the keypad.
At most occasions, data should be obtained by polling the flow mete with a command, the flow meter will
respond with what the master asks.
DTI-1 can also set to automatically output data at a period which is programmable.
The DTI-1 also has a special command sets to facilitate the use of the flow meter in a GSM network.
1.1 The MODBUS protocol
Both the two formats of the MODBUS protocol can be supported.
A software switch located at the window number 63(shorted as M63 after) select MODBUS-ASCII or
MODBUS-RTU will be in functioning.
The default option is MODBUS-ASCII format.
DTI-1 can only support MODBUS functions code 3 and code 6, i.e. reading registers and writing a 
register.
For example, reading the registers from REG0001 to REG0010 in the unit #1 (ultrasonic flow meter) under
the MODBUS-RTU format, the command could be as following
01
03
00
00
00
0A
C5
CD
（hex）
Unit
Function
start
REG
Numbers of REGs
Check-sum
While under the MODBUS-ASCII format, the command could be
:01030000000AF2(CR and LF)
Details about the standard MODBUS protocol will not be studied in this manual; please the users find them
on other related materials.
By default, the RS232/RS485 will setup with 9600,none,8,1(9600bd，none parity，8 data bits， 1 stop bit)
1.1.1 MODBUS REGISTERS TABLE


MODBUS REGISTERS TABLE for DTI-1
（please take notice the difference with the water meter MODBUS table
2
）
REGISTER
NUMB
ER
VARIABLE NAME
FORMAT
NOTE
0001-0002
2
Flow Rate
REAL4
Unit:
m3/h
0003-0004
2
Energy Flow Rate
REAL4
Unit:
GJ/h
0005-0006
2
Velocity
REAL4
Unit:
m/s
0007-0008
2
Fluid sound speed
REAL4
Unit:
m/s
0009-0010
2
Positive accumulator
LONG
Unit is selected by M31, and
depends on totalizer multiplier
0011-0012
2
Positive decimal fraction
REAL4
Same unit as the integer part
0013-0014
2
Negative accumulator
LONG
Long is a signed 4-byte integer,
lower byte first
0015-0016
2
Negative decimal fraction
REAL4
REAL4 is a format of Singular
IEEE-754 number, also called
FLOAT
0017-0018
2
Positive energy accumulator
LONG
0019-0020
2
Positive energy decimal fraction
REAL4
0021-0022
2
Negative energy accumulator
LONG
0023-0024
2
Negative energy decimal fraction
REAL4
0025-0026
2
Net accumulator
LONG
0027-0028
2
Net decimal fraction
REAL4
0029-0030
2
Net energy accumulator
LONG
0031-0032
2
Net energy decimal fraction
REAL4
0033-0034
2
Temperature #1/inlet
REAL4
Unit: C
0035-0036
2
Temperature #2/outlet
REAL4
Unit: C
0037-0038
2
Analog input AI3
REAL4
0039-0040
2
Analog input AI4
REAL4
0041-0042
2
Analog input AI5
REAL4
0043-0044
2
Current input at AI3
REAL4
In unit mA
0045-0046
2
Current input at AI3
REAL4
In unit mA
0047-0048
2
Current input at AI3
REAL4
In unit mA
0049-0050
2
System password
Writable。00H for unloc
BCD
k
0051
1
Password for hardware
Writable。“A55Ah” for unloc
BCD
k
0053-0055
3
Calendar (date and time)
Writable。6 Bytes of BCD stands
SMHDMY，lower byte firs
BCD
t
0056
1
Day+Hour for Auto-Save
Writable。For example 0512H
stands Auto-save on 12:00 on 5th。
0012H for 12:00 on everyday
BCD
。
0059
1
Key to input
INTEGER
Writable
0060
1
Go to Window #
Writable
INTEGER
。
0061
1
LCD Back-lit lights for number of
Writable。In unit secon
INTEGER
d


3
seconds
0062
1
Times for the beeper
INTEGER
Writable。Max 255
0062
1
Pulses left for OCT
INTEGER
Writable。Max 65535
0072
1
Error Code
BIT
16bits, see note 4
0077-0078
2
PT100 resistance of inlet
REAL4
In unit Ohm
0079-0080
2
PT100 resistance of outlet
REAL4
In unit Ohm
0081-0082
2
Total travel time
REAL4
In unit Micro-second
0083-0084
2
Delta travel time
REAL4
In unit Nino-second
0085-0086
2
Upstream travel time
REAL4
In unit Micro-second
0087-0088
2
Downstream travel time
REAL4
In unit Micro-second
0089-0090
2
Output current
REAL4
In unit mA
0092
1
Working step and
Signal Quality
INTEGER
The high byte is the step and low for
signal quality，range 00-99，the
larger the better.
0093
1
Upstream strength
INTEGER
Range 0-2047
0094
1
Downstream strength
INTEGER
Range 0-2047
0096
1
Language used in user interface
INTEGER
0 : English，1:Chinese
Other language will be supported
later
0097-0098
2
The rate of the measured travel time by
the calculated travel time.
REAL4
Normal 100+-3%
0099-0100
2
Reynolds number
REAL4
0101-0102
2
Pipe Reynolds factor
REAL4
0103-0104
2
Working Timer
LONG
unsigned，in second
0105-0106
2
Total working time
LONG
unsigned，in second
0105-0106
2
Total power on-off time
LONG
Unsigned
0113-0114
2
Net accumulator
REAL4
In Cubic Meter，float
0115-0116
2
Positive accumulator
REAL4
In Cubic Meter，float
0117-0118
2
Negative accumulator
REAL4
In Cubic Meter，float
0119-0120
2
Net energy accumulator
REAL4
In GJ，float
0121-0122
2
Positive energy accumulator
REAL4
In GJ，float
0123-0124
2
Negative energy accumulator
REAL4
In GJ，float
0125-0126
2
Flow for today
REAL4
In Cubic Meter，float
0127-0128
2
Flow for this month
REAL4
In Cubic Meter，float
0129-0130
2
Manual accumulator
LONG
0131-0132
2
Manual accumulator decimal fraction
REAL4
0133-0134
2
Batch accumulator
LONG
0135-0136
2
Batch accumulator decimal fraction
REAL4
0137-0138
2
Flow for today
LONG
0139-0140
2
Flow for today decimal fraction
REAL4
0141-0142
2
Flow for this month
LONG
0143-0144
2
Flow for this month decimal fraction
REAL4


4
0145-0146
2
Flow for this year
LONG
0147-0148
2
Flow for this year decimal fraction
REAL4
0158
1
Current display window
INTEGER
0165-0166
2
Failure timer
LONG
In unit second
0173-0174
2
Current output frequency
REAL4
Unit：Hz
0175-0176
2
Current output with 4-20mA
REAL4
Unit：mA
0181-0182
2
Temperature difference
REAL4
Unit：C
0183-0184
2
Lost flow for period of last power off
REAL4
Unit：Cubic Meter
0185-0186
2
Clock coefficient
REAL4
Should less than 0.1
0187-0188
2
Total time for Auto-Save
REAL4
Time to save by 0056
0189-0190
2
POS flow for Auto-Save
REAL4
Time to save by 0056
0191-0192
2
Flow rate for Auto-Save
REAL4
Time to save by 0056
0221-0222
2
Inner pipe diameter
REAL4
In millimeter
0229-0230
2
Upstream delay
REAL4
In microsecond
0231-0232
2
Downstream delay
REAL4
In microsecond
0233-0234
2
Calculated travel time
REAL4
In microsecond
0257-0288
32
LCD buffer
BCD
0289
1
LCD buffer pointer
INTEGER
0311
2
Worked time for today
LONG
Unsigned, in seconds
0313
2
Worked time for this month
LONG
Unsigned, in seconds
1437
1
Unit for flow rate
INTEGER
See note 5
1438
1
Unit for flow totalizer
INTEGER
Range 0~7,see note 1
1439
1
Multiplier for totalizer
INTEGER
Range 0~7,see note 1
1440
1
Multiplier for energy accumulator
INTEGER
Range 0~10,see note 1
1441
1
Unit for energy rate
INTEGER
0=GJ
1=Kcal 2=KWh，3=BTU
1442
1
Device address
INTEGER
1451
2
User scale factor
REAL4
1521
2
Manufacturer scale factor
REAL4
Read only
1529
2
Electronic serial number
BCD
High byte first
Note ：(1) The internal accumulator is been presented by a LONG number for the integer part together with
a REAL number for the decimal fraction. In general uses, only the integer part needs to be read. Reading
the fraction can be omitted. The final accumulator result has a relation with unit and multiplier. Assume N
stands for the integer part (for the positive accumulator, the integer part is the content of REG 0009, 0010,
a 32-bits signed LONG integer,), Nf stands for the decimal fraction part (for the positive accumulator, the
fraction part is the content of REG 0011, 0012, a 32-bits REAL float number,), n stands for the flow
multiplier (REG 1439).
then
The final positive flow rate=(N+Nf ) ×10n-3
(in unit decided by REG 1438）。
The meaning of REG 1438 which has a range of 0~7 is as following:
0
cubic meter
(m3)
1
liter
(L)


5
2
American gallon
(GAL)
3
imperial gallon
(IGL)
4
American million gallon
(MGL)
5
Cubic feet
(CF)
6
American oil barrel
(1 barrel =42gallon) (OB)
7
Imperial oil barrel
(IB)
While
The energy flow rate =(N+Nf )×10n-4（unit decided by REG 1441）
n=(0~10) is the energy multiplier which is in REG1440
(2) Other variables are not given here. Call us if you have a need.
(3) Please note there are many of the data that is not applicable for the non-energy measurement
users. These none-energy-related registers only serves for the intension of only one unique register table
provided both with flow meter and energy meat.
(4) Meaning in error code
Bit0
no received signal
Bit1
low received signal
Bit2
poor received signal
Bit3
pipe empty
Bit4
hardware failure
Bit5
receiving circuits gain in adjusting
Bit6
frequency at the frequency output over flow
Bit7
current at 4-20mA over flow
Bit8
RAM check-sum error
Bit9
main clock or timer clock error
Bit10
parameters check-sum error
Bit11
ROM check-sum error
Bit12
temperature circuits error
Bit13
reserved


6
Bit14
internal timer over flow
Bit15
analog input over range
Please try to override these energy-related bits first when in flow-only measurement,
(5) Unit code for flow rate
0
Cubic meter/second
1
Cubic meter
/minute
2
Cubic meter /hour
3
Cubic meter /day
4
liter/second
5
liter /minute
6
liter /hour
7
liter /day
8
American
gallon/second
9
American gallon
/minute
10
American gallon /hour
11
American gallon /day
12
Imperial gallon/second
13
Imperial gallon
/nimute
14
Imperial gallon /hour
15
Imperial gallon /day
16
American million
gallon/second
17
American million
gallon /minute
18
American million gallon
/hour
19
American million gallon/day
20
Cubic feet/second
21
Cubic feet/minute
22
Cubic feet/hour
23
Cubic feet/day
24
American oil
barrel/second
25
American oil
barrel/minute
26
American oil
barrel/hour
27
American oil barrel/day
28
Imperial oil barrel/second
25
Imperial oil
barrel/minute
26
Imperial oil barrel/hour
27
Imperial oil barrel/day
1.1.2 REGISTER TABLE for the DATE accumulators
（1）REGISTER for accumulators by day
Accumulator data for every past day are stored in a loop queue. Every day has 16 bytes of data and there
are 64 days in total. The current pointer which has a range of 0~63 for the day is in REG 0162. if the pointer
is decreased by 1 when the pointer is 0, then new pointer value will be 63. Assume REG 0162= 1, the data
for yesterday are in REG 2825~2832, the data for the day before yesterday are in REG2817-2824, and the
data for the day of 2 days ago are in REG 3321-3328.
REGISTER TABLE for the DAY accumulators
Block No.
Register
number
variable
format
Note
n/a
0162
1
Data pointer
Integer
Range:0~63
0
2817
1
Day and Error Code
BCD
Day in high byte
2818
1
Month and year
BCD
Year in high byte
2819-2820
2
Total working time
LONG
2821-2822
2
Net total flow for the day
REAL4
2823-2824
2
Net total energy for the day
REAL4
2825
1
Day and Error Code
BCD
Day in high byte
2826
1
Month and year
BCD
Year in high byte


7
1
2827-2828
2
Total working time
LONG
2829-2830
2
Net total flow for the day
REAL4
2831-2832
2
Net total energy for the day
REAL4
。。。。
。。。。。。。。。。 。。。。。。 。。。。。。。。。。。。。。
。。。。。。
。。。。。。。。。。。。。。。。。。。。
6 3
3321-3328
8
Data block No.63
Note：See the meaning of the error code above.
(2) REGISTER for accumulators by month
The structure of month accumulator is the same as that of the day，please refer to related paragraph。The
difference is there are only 32 data blocks for the month accumulator, and day variable always has a value
of 0.
REGISTER TABLE for the month accumulators
Block No.
Register
number
Variable
format
note
n/a
0163
1
Data pointer for the month
Integer
Range: 0~63
0
3329
1
Error Code
BCD
3330
1
Month and year
BCD
Year in high byte
3331-3332
2
Total working time
LONG
3333-3334
2
Net total flow for the month
REAL4
3335-3336
2
Net total energy for the
month
REAL4
1
3337
1
Error Code
BCD
3338
1
Month and year
BCD
Year in high byte
3339-3340
2
Total working time
LONG
3341-3342
2
Net total flow for the month
REAL4
3343-3344
2
Net total energy for the
month
REAL4
。。。。
。。。。。。。。。。 。。。。。。 。。。。。。。。。。。。。。 。。。。。。
。。。。。。。。。。。。。。。。。。。。
31
3577-3584
8
Data block No. 31
(3) There is no direct data for the year, data for the year could be conducted from the data of the months.
5.1.3 REGISTER for power-on and power-off
With every t power-on and power-off, the new generation flow meter will record data about the time,
duration, statue byte and the flow rate into a data block. Every data block consists 32 bytes of data.
There are as many as 16 blocks of data can be recorded, for 16 times of power-on and 16 times of
power-off. The data blocks are in a structure of loop queue. The 16th data block will override the first block


8
by default. The location of the current block is presented in the data pointer. The current power-on data
block is pointed by the decease by 1 of the pointer.
MODBUS registers table for the power-on and power-off.
Block No.
Register
No.
Variable
Format
Note
n/a
0164
1
Pointer
Integer
Range:0~31
0
3585
1
Power-on second and
minute
BCD
Second in low byte, minute in high
3586
1
Power-on hour and day
BCD
Hour in low byte, day in high
3587
1
Power-on month and year
BCD
Month in low byte, year in high
3588
1
Power-on error code
BIT
B15 stand for corrected lost flow.
3589
1
Power-off second and
minute
BCD
Second in low byte, minute in high
3590
1
Power-off hour and day
BCD
Hour in low byte, day in high
3591
1
Power-off month and year
BCD
Month in low byte, year in high
3592
1
Power-off error code
BIT
B15 stand for corrected lost flow
3593-3594
2
Flow rate when power on
REAL4
Flow rate after 60 seconds when power
on
3595-3596
2
Flow rate when power off
REAL4
3597-3598
2
Time duration when off
LONG
In seconds
3599-3600
2
Corrected lost flow when off
REAL4
In cubic meters
1
3601
1
Power-on second and
minute
BCD
Second in low byte, minute in high
3602
1
Power-on hour and day
BCD
Hour in low byte, day in high
3603
1
Power-on month and year
BCD
Month in low byte, year in high
3604
1
Power-on error code
BIT
B15 stand for corrected lost flow.
3605
1
Power-off second and
minute
BCD
Second in low byte, minute in high
3606
1
Power-off hour and day
BCD
Hour in low byte, day in high
3607
1
Power-off month and year
BCD
Month in low byte, year in high
3608
1
Power-off error code
BIT
B15 stand for corrected lost flow
3609-3610
2
Flow rate when power on
REAL4
Flow rate after 60 seconds when power
on
3611-3612
2
Flow rate when power off
REAL4
3613-3614
2
Time duration when off
LONG
In seconds
3615-3616
2
Corrected lost flow when off
REAL4
In cubic meters
。。。。
。。。。。。。。。 。。。
。。。。。。
。。。。。。。。。。。。。。。。。。。。
31
3825-3840
16
The 32nd data block
1.2 The FUJI extended communication protocol


DTI-1 is compatible with the TUF7-FUJI extended communication protocol which used in our previous 
Version7 ultrasonic flow meters. This protocol is a set of basic commands that are in ASCII format, ending 
with a carriage return (CR) and line feed (LF), For most of the commands, The line feed (LF) should be 
9
better omitted for fast responding.
Command
Meaning
Data format
note
DQD(cr)
0
Returns flow rate per day
note
±d.ddddddE±dd(cr)
1
DQH(cr)
Return flow rate per hour
±d.ddddddE±dd(cr)
DQM(cr)
Return flow rate per minute
±d.ddddddE±dd(cr)
DQS(cr)
Return flow rate per second
±d.ddddddE±dd(cr)
DV(cr)
Return fluid velocity
±d.ddddddE±dd(cr)
DI+(cr)
±dddddddE±d(cr)note
Return positive totalizer
2
DI-(cr)
Return negative totalizer
±dddddddE±d(cr)
DIN(cr)
Return net totalizer
±dddddddE±d(cr)
DIE(cr)
Return net thermal energy totalizer
±dddddddE±d(cr)
DIE+(cr)
Return positive energy totalizer
±dddddddE±d(cr)
DIE-(cr)
Return negtive energy totalizer
±dddddddE±d(cr)
DIT(cr)
Return net total flow for today
±dddddddE±d(cr)
DIM(cr)
Return net total flow for this month
±dddddddE±d(cr)
DIY(cr)
Return net total flow for this year
±dddddddE±d(cr)
DID(cr)
Return the ID number/address
ddddd(cr)
5 bytes long
E(cr)
Return instantaneous Caloric Value
±d.ddddddE±dd(cr)
DL(cr)
Return signal strength and signal quality
UP:dd.d,DN:dd.d,Q=dd(cr)
DS(cr)
Return the percentage of AO output
±d.ddddddE±dd(cr)
DC(cr)
Return present error code
Note 3
DA(cr)
TR:s,RL:s(cr)note
OCT and RELAY alarm signal
4
DT(cr)
Return the present date and time
yy-mm-dd,hh:mm:ss(cr)
Time@TDS1=(cr)
Set date and time yy-mm-dd,hh:mm:ss
M@(cr)
M@(cr)note
Send a key value as if a key is pressed.
@ is the key value
5
LCD(cr)
Returns current window content
LOCK0(cr)
Unlock the system
Has nothing to do with the original password.
LOCK1(cr)
Lock the system
Can be opened by press ENT key
MENUXX(cr)
Go to window XX
LanguageX(cr)
X=0 for English, 1 for Chinese
2 for Italy, if applicable
3 for Korea, if applicable
4 for French, if applicable
5 for Germany，if applicable
6 for Spanish, if applicabl
Select interface language
e


10
BaudRateX(cr)
Change baud rate
X=0~7, will set to 19200, 14400,
9600,4800,2400,1200,600,300
C1(cr)
OCT close
C0(cr)
OCT open
R1(cr)
RELAY(OCT2) close
R0(cr)
RELAY(OCT2) open
FOdddd(cr)
Force the FO to output a frequency of dddd HZ
Fdddd(cr)(lf)
AOa(cr)
Output current ‘a’ mA at the AO output terminal.
AOa(cr)(lf)Note 6
BA1(cr)
Return the resistance for T1
±d.ddddddE±dd(cr)(lf)
BA2(cr)
Return the resistance for T2
±d.ddddddE±dd(cr)(lf)
BA3(cr)
Return current value of AI3 (0~20mA)
±d.ddddddE±dd(cr)(lf)
BA4(cr)
Return current value of AI4 (0~20mA)
±d.ddddddE±dd(cr)(lf)
BA5(cr)
Return current value of AI5 (0~20mA)
±d.ddddddE±dd(cr)(lf)
AI1(cr)
Return temperature at T1 input
±d.ddddddE±dd(cr)(lf)
AI2(cr)
Return temperature at T2 input
±d.ddddddE±dd(cr)(lf)
AI3(cr)
Return temperature /pressure value of AI3
±d.ddddddE±dd(cr)(lf)
AI4(cr)
Return temperature /pressure value of AI4
±d.ddddddE±dd(cr)(lf)
AI5(cr)
Return temperature /pressure value of AI5
±d.ddddddE±dd(cr)(lf)
ESN(cr)
Return the ESN (electronic serial number) of the
flow meter
ddddddd(cr)(lf) note 7
N
Prefix
of an IDN-addressing-based networking,
The IDN address is byte, range 0-253
Note 8
W
Prefix
of an IDN-addressing-based networking,
The IDN address is word, range 0-65535
Note 8
P
Prefix of any commands for returns with
check-sum
&
Commands connector to make a compounding
command in one line.
Result commands should not exceed 253
bytes long.
RING(cr)(lf)
Handshaking request from a modem
ATA(CR)(lf)
OK(cr)
Acknowledgement from a modem.
No action
Handshaking from the flow meter to modem.
AT(CR)(LF)
GA(cr)
Special command for GSM network.
note９
GB(cr)
Special command for GSM network.
note９
GC(cr)
Special command for GSM network
note９
Note:
0.（cr）stand for carriage return, its ASCII value is 0DH. (lf) stand for line feed, its ASCII value is 0AH.
1．d stand for a digit number of 0~9, 0 is expressed as +0.000000E+00
2．d stand for digit 0~9, the number before ‘E’ is an integer.


11
3．Working status code, 1~6 letters, refer to error code related chapter.
4．‘s’ is ‘ON’,’OFF’ or ‘UD’
For example ‘TR:ON,RL:ON’ means the OCT and RELAY are closed
‘TR:UD,RL:UD” means the OCT and RELAY are not used.
5．@ stand for key value, for example, value 30H means key ‘0’. The command ‘M4(cr)’ acts just like the
number 4 key on the keypad was pressed.
6． ’a’ stands for the output current value. The maximum value should not exceed 20.0 For example
AO2.34567, AO0.2
7． ’dddddddd’
stands for the Electronic Serial Number
8． If there are more than one devices in a network, all the basic command must be prefixed with ‘N’ or ‘W’,
otherwise multiple flow meter may reply to the same request, and thus a conflict may occurs.
9.
The returns by the special command for GSM networks contend Chinese characters.
1.2.1Command prefixes and the command connector
(1) The ‘P’ prefix
The ‘P’ prefix can be added before every basic command to have the returned message with a two digits
check-sum. The check-sum is obtained by a binary addition.
For example, if the command
DI+(CR)
(44H,49H,2BH,0DH in binary numbers）will bring a return like +1234567E+0m3 (CR)
(2BH,31H,32H,33H,34H,35H,36H,37H,45H,2BH,30H,6DH,33H,20H,0DH,0AH in binary numbers), then
the PDI+(CR) will brings a return like +1234567E+0m3 !F7(CR), after the character‘!’ are the
check-sum in ASCII format(2BH+31H+32H+33H+34H+35H+
36H+37H+45H+2BH+30H+6DH+33H+20H=(2)F7H)
Pay attention to that there may be no characters or only spaces before the character ‘!’.
(2) The ‘N’ prefix
The usage of prefix ‘N‘ goes like:
N + single byte address + basic command.
For example if the address number 88 flow meter is going to be addressed, the command should like:
NXDV(CR), the decimal value of X should be 88.
The prefix W is strongly recommended for new users.
(3) The ‘W’ prefix
Usage: W + character string address + basic command
The value of the character string should have a value in the range of 0~65535, except for the value of
13
（0DH carriage return），10（0AH line feed ），42（2AH *），38（26H&）.


For example, if the velocity of number 12345 flow meter is wanted, the command can be like:
W12345DV(CR), (57H,31H,32H,33H,34H,35H,44H,56H,0DH in binary numbers
12
)
(4) The command connecter ‘&’
The command connecter ‘&’ adds several basic commands into a one-line compound command. The
compound command should not exceed a length of over 253 characters. The prefix ‘P’ should be added
before every basic command, to make the returned results having a check-sum.
For example, if the 1)flow rate 2)velocity 3)positive totalizer 4) net energy totalizer 5) the AI1 input 6) the
AI2 input of the address number 4321 flow meter are wanted to return with check-sum, the one-line
command is like:
W4321PDQD&PDV&PDI+&PDIE&PBA1&PAI2(CR)
The returned data are:
+0.000000E+00m3/d!AC(CR)
+0.000000E+00m/s!88(CR)
+1234567E+0m3 !F7(CR)
+0.000000E+0GJ!DA(CR)
+7.838879E+00mA!59
+3.911033E+01!8E(CR)
Any command can be connected together. For example, if a serious key want be sent, to set up the outer
diameter to 1234.567 mm, a compound command will be
MENU11&M1&M2&M3&M4&M:&M5&M6&M7&M=(CR)
1.3 the compatible communication protocols
Flow meters made by Huizhong have more than 10 different communications protocols. For the easier 
replacement of a water meter, most of these protocols are realized in DTI-1 flow meters. Here only one of 
them, the default for compatible protocols CRL-61D (D<=50mm), is given for reference.
These protocols are selectable by Menu63, after the selection of MOBUS-ASCI, or MODBUS-RTU
protocols.
interface：RS232，RS485
baud rate：9600 by default，select other 15 different baud rate by Menu 62
parity：NONE, EVEN, ODD can be chosen from Menu 62
Data bits：8
Stop bits: 1, 2
In the following explanation:


13
XXh stands for the address (or network ID)of the instrument, range:00h-FFh.
YYh stands for the new address that will be assigned, range:00h-FFh.
ZZh the check-sum, which is obtained by means of binary addition of all the data bytes (take notice
to that the addition is for the data bytes, not the controlling and commands bytes, and
the carry over 0ffh is discarded.
H stands for that the number is a hexadecimal number.
All five command are like following:
(1) read water meter data (command 4A）
Format: 2Ah XXh 4Ah
Answer: 26h XXh 4Ah
LL(BCD coded ）ZZh
In the above, the contents of LL(BCD) are formatted as in the following table:
(2) Reading the recorded meter data (command 49)
Format：2Ah XXh 49h
Answer:
26h XXh 49h
LL（BCD 码） ZZh
The difference between the command 4A and command 49 is that the late command reads out the
data which are recorded in the meter by the time which is defined by command 4C.
(3) Change the address of the meter (command 4B)
Format： 2Ah XXh 4Bh YYh
Answer:
26h XXh 4Bh YYh
If XXh=YYh, this command can be used to do a loop test the net work, or to scan and find the
existed meters in the network. Please pay attention to that the network may lose meters if this
command is used in a noisy network.
(4) Change or assign a time for meter data recording (command 4C)
Format:
2Ah XXh 4Ch DDh HHh
Answer:
26h XXh 4Ch DDh HHh MMh ZZh
DDh stands for the day, HHh for hour,
MM for minute，data are in BCD code.
Position
Content
Bytes
Note
1~4
Flow rate
4
The actual value is divided by 1000, unit in cubic meter per hour.
5~8
Positive total flow
4
The actual value divided by 10, unit in cubic meter
9~12
Total time
4
Unit in hour
13
Error code
1
See table below


14
DD is the day of this month, for example: 2Ah 86h 4Ch 12h 15h stands for assigning a recording
time for the number 86 meter 86. the meter will record the flow rate, total net flow, the working
timer and the error code when time is 15:00 the 12th of this month. The recorded date will be
read out by command 49.
If DD＝0, it stands that the data recording will take place by 15:00 for every day.
(5) Standard date and time broadcasting （command 4D）
Format: 2Ah AAh 4Dh ssmmhhDDMMYY
Answer: no answer
In above, ssmmhhDDMMYY is the date and time in BCD format.
Diagnostic code:
00h stands that the system is working normally.
02h stands for the pipe may be empty or meter works improperly.
05h stand for there exist hardware failure, repair may needed.
1.4 Key Value Table
The key values are used in a network application. By use of the key value and a command ‘M’, we can
operate the flow meter through the network on a computer or other kind of terminals. For example, the
command ‘M0(cr)’ acts just like the zero key on the keypad was pressed.
Key
Key value
(headecimal)
Key value
(decimal)
ASCII
value
key
Key value
(headecimal)
Key value
(decimal)
ASCII
value
0
30H
48
0
8
38H
56
8
1
31H
49
1
9
39H
57
9
2
32H
50
2
.
3AH
58
:
3
33H
51
3
◄
3BH
59
;
4
34H
52
4
MENU
3CH
60
<
5
35H
53
5
ENT
3DH
61
=
6
36H
54
6
▲/+
3EH
62
>
7
37H
55
7
▼/-
3FH
63
?
