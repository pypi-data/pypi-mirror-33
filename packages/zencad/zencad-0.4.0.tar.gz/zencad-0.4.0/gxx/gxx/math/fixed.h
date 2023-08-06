#ifndef GXX_FIXED_POINT_TYPES_H
#define GXX_FIXED_POINT_TYPES_H

#include <inttypes.h>
#include <gxx/print.h>

class fxuint16_t {
public:
	uint16_t data;
	fxuint16_t() = default;

	fxuint16_t operator+ (fxuint16_t rhs) {
		fxuint16_t ret;
		ret.data = data + rhs.data; 
		return ret;
	}


	fxuint16_t& operator+= (fxuint16_t rhs) {
		data += rhs.data; 
		return *this;
	}

	fxuint16_t operator* (fxuint16_t rhs) {
		uint32_t res = data * rhs.data;
		fxuint16_t ret;
		ret.data = *reinterpret_cast<uint16_t*>(reinterpret_cast<uint8_t*>(&res) + 1);
		return ret;
	}

	fxuint16_t(int8_t i) : data(i << 8 ) {}
	fxuint16_t(int16_t i) : data(i << 8 ) {}
	fxuint16_t(int32_t i) : data(i << 8 ) {}
	fxuint16_t(int64_t i) : data(i << 8 ) {}
	fxuint16_t(uint8_t i) : data(i << 8 ) {}
	fxuint16_t(uint16_t i) : data(i << 8 ) {}
	fxuint16_t(uint32_t i) : data(i << 8 ) {}
	fxuint16_t(uint64_t i) : data(i << 8 ) {}
	fxuint16_t(float f) : data(f * 256 + 0.5) {}
	fxuint16_t(double f) : data(f * 256 + 0.5) {}

	unsigned int printTo(gxx::io::ostream& o) const {
		return gxx::print(o, (float)data / 256);
	}
};


class fxuint32_t {
public:
	uint32_t data;
	fxuint32_t() = default;

	fxuint32_t operator+ (fxuint32_t rhs) {
		fxuint32_t ret;
		ret.data = data + rhs.data; 
		return ret;
	}

	fxuint32_t& operator+= (fxuint32_t rhs) {
		data += rhs.data; 
		return *this;
	}

	fxuint32_t operator* (fxuint32_t rhs) {
		uint64_t res = (uint64_t)data * rhs.data;
		fxuint32_t ret;
		ret.data = *reinterpret_cast<uint32_t*>(reinterpret_cast<uint16_t*>(&res) + 1);
		return ret;
	}

	fxuint32_t(int8_t i) : data(i << 16 ) {}
	fxuint32_t(int16_t i) : data(i << 16 ) {}
	fxuint32_t(int32_t i) : data(i << 16 ) {}
	fxuint32_t(int64_t i) : data(i << 16 ) {}
	fxuint32_t(uint8_t i) : data(i << 16 ) {}
	fxuint32_t(uint16_t i) : data(i << 16 ) {}
	fxuint32_t(uint32_t i) : data(i << 16 ) {}
	fxuint32_t(uint64_t i) : data(i << 16 ) {}
	fxuint32_t(float f) : data(f * 65536 + 0.5) {}
	fxuint32_t(double f) : data(f * 65536 + 0.5) {}

	unsigned int printTo(gxx::io::ostream& o) const {
		return gxx::print(o, (float)data / 65536);
	}
};

#endif