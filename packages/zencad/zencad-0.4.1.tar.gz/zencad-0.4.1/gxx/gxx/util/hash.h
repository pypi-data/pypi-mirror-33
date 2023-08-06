#ifndef GENOS_HASH_H
#define GENOS_HASH_H

//Функции для вычисления хэшей.

#include <string.h>
#include <inttypes.h>

#ifndef GXX_DEFAULT_SEED
#	define GXX_DEFAULT_SEED 0xABCDEFAB
#endif

namespace gxx {

	//extern uint32_t GXX_DEFAULT_SEED; 

	template <typename T> 
	inline size_t hash(const T& other, uint32_t seed = GXX_DEFAULT_SEED) {
		return other.hash(seed);
	}

	inline size_t hash(const char * p, size_t len, uint32_t seed = GXX_DEFAULT_SEED) {
		size_t h = seed;
		for (uint32_t i = 0; i < len; ++i)
			h = 31 * h + p[i];
		return h;
	}

	inline size_t hash(int8_t val, uint32_t seed = GXX_DEFAULT_SEED) { return val ^ seed;}
	inline size_t hash(int16_t val, uint32_t seed = GXX_DEFAULT_SEED) { return val ^ seed; }
	inline size_t hash(int32_t val, uint32_t seed = GXX_DEFAULT_SEED) { return val ^ seed; }
	inline size_t hash(int64_t val, uint32_t seed = GXX_DEFAULT_SEED) { return val ^ seed; }
	inline size_t hash(uint8_t val, uint32_t seed = GXX_DEFAULT_SEED) { return val ^ seed; }
	inline size_t hash(uint16_t val, uint32_t seed = GXX_DEFAULT_SEED) { return val ^ seed; }
	inline size_t hash(uint32_t val, uint32_t seed = GXX_DEFAULT_SEED) { return val ^ seed; }
	inline size_t hash(uint64_t val, uint32_t seed = GXX_DEFAULT_SEED) { return val ^ seed; }

	inline size_t hash(const char* val, uint32_t seed = GXX_DEFAULT_SEED) { return hash(val,strlen(val),seed); }

	static uint32_t sdbm_hash(const void *data, size_t size) {
        uint32_t hash = 0;
        uint8_t* it = (uint8_t*)data;
        uint8_t* eit = (uint8_t*)data + size;

        for(;it != eit; ++it)
            hash = *it + (hash << 6) + (hash << 16) - hash;

        return hash;
    }

    static uint32_t sdbm_hash(const char *str) {
        uint32_t hash = 0;
        char c;

        while (c = *str++)
            hash = c + (hash << 6) + (hash << 16) - hash;

        return hash;
    }

    static uint32_t sdbm_hash(const std::string& str) {
    	return sdbm_hash(str.data(), str.size());
    }

}

#endif