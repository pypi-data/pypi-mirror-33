#ifndef GXX_UTIL_CRC_H
#define GXX_UTIL_CRC_H

static inline void strmcrc8(uint8_t* crc, char c) {
	*crc ^= c;
	for (int i = 0; i < 8; i++)
		*crc = *crc & 0x80 ? (*crc << 1) ^ 0x31 : *crc << 1;
}

#endif