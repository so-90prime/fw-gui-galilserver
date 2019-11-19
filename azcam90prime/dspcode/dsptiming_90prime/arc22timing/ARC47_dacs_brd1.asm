; ARC47_dacs_brd1.asm
; ARC47 4 channel video board DACS table
; second installed board
; 04Sep13 last change MPL

; Commands for the ARC-47 video board 
	DC	VID1+$0C0004                    ; Normal Image data D17-D2

; Gain : $0D000g, g = 0 to %1111, Gain = 1.00 to 4.75 in steps of 0.25
	DC	VID1+$0D0000+VGAIN
	DC	VID1+$0C0100+VSPEED             ; time constant

; Initialize the ARC-47 DAC For DC_BIAS
	DC	VID1+DAC_ADDR+$000000		; Vod0,pin 52
	DC	VID1+DAC_RegD+DAC_VOD5
	DC	VID1+DAC_ADDR+$000004		; Vrd0,pin 13
	DC	VID1+DAC_RegD+DAC_VRD5	
	DC	VID1+DAC_ADDR+$000008		; Vog0,pin 29
	DC	VID1+DAC_RegD+DAC_VOG5		
	DC	VID1+DAC_ADDR+$00000C		; Vabg,pin 5
	DC	VID1+DAC_RegD+DAC_VRSV5
	
	DC	VID1+DAC_ADDR+$000001		; Vod1,pin 32
	DC	VID1+DAC_RegD+DAC_VOD6
	DC	VID1+DAC_ADDR+$000005		; Vrd1,pin 55
	DC	VID1+DAC_RegD+DAC_VRD6	
	DC	VID1+DAC_ADDR+$000009		; Vog1,pin 8
	DC	VID1+DAC_RegD+DAC_VOG6		
	DC	VID1+DAC_ADDR+$00000D		; Vrsv1,pin 47
	DC	VID1+DAC_RegD+DAC_VRSV6

	DC	VID1+DAC_ADDR+$000002		; Vod2,pin 11
	DC	VID1+DAC_RegD+DAC_VOD7
	DC	VID1+DAC_ADDR+$000006		; Vrd2,pin 35
	DC	VID1+DAC_RegD+DAC_VRD7	
	DC	VID1+DAC_ADDR+$00000A		; Vog2,pin 50
	DC	VID1+DAC_RegD+DAC_VOG7		
	DC	VID1+DAC_ADDR+$00000E		; Vrsv2,pin 27
	DC	VID1+DAC_RegD+DAC_VRSV7
	
	DC	VID1+DAC_ADDR+$000003		; Vod3,pin 53
	DC	VID1+DAC_RegD+DAC_VOD8
	DC	VID1+DAC_ADDR+$000007		; Vrd3,pin 14
	DC	VID1+DAC_RegD+DAC_VRD8	
	DC	VID1+DAC_ADDR+$00000B		; Vog3,pin 30
	DC	VID1+DAC_RegD+DAC_VOG8	
	DC	VID1+DAC_ADDR+$00000F		; Vrsv3,pin 6
	DC	VID1+DAC_RegD+DAC_VRSV8
		
	DC	VID1+DAC_ADDR+$000010		; Vod4,pin 33
	DC	VID1+DAC_RegD+DAC_VSCP2
	DC	VID1+DAC_ADDR+$000011		; Vrd4,pin 56
	DC	VID1+DAC_RegD+DAC_VRD4	
	DC	VID1+DAC_ADDR+$000012		; Vog4,pin 9
	DC	VID1+DAC_RegD+DAC_VOG4	
	DC	VID1+DAC_ADDR+$000013		; Vrsv4,pin 48
	DC	VID1+DAC_RegD+DAC_VRSV4

; Initialize the ARC-47 DAC For Video Offsets
	DC	VID1+DAC_ADDR+$000014
	DC	VID1+DAC_RegD+OFFSET+OFFSET4
	DC	VID1+DAC_ADDR+$000015
	DC	VID1+DAC_RegD+OFFSET+OFFSET5
	DC	VID1+DAC_ADDR+$000016
	DC	VID1+DAC_RegD+OFFSET+OFFSET6
	DC	VID1+DAC_ADDR+$000017
	DC	VID1+DAC_RegD+OFFSET+OFFSET7

; end of ARC47_dacs_brd1.asm