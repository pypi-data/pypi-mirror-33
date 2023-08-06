#include <gxx/util/hexascii.h>
#include <gxx/util/asciiconvert.h>

namespace gxx {
	std::string hexascii_encode(const uint8_t *indata, size_t size) {
		std::string ret;
		ret.resize(size*2);
		const uint8_t* eit = indata + size; 
		uint8_t* oit = (uint8_t*)&ret[0];
		for(const uint8_t* it = indata; it != eit; ++it) {
			*oit++ = byte2sym((*it & 0xF0) >> 4);
			*oit++ = byte2sym(*it & 0xF);
		}
		return ret;
	}

	std::string hexascii_encode(const std::string& str) {
		return hexascii_encode((const uint8_t*)str.data(), str.size());
	}
}