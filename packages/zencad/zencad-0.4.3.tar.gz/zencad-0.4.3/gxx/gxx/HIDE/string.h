#ifndef GENOS_STRING_H
#define GENOS_STRING_H

#include <gxx/util/setget.h>
#include <gxx/util/numconvert.h>

#include <string.h>
#include <stdarg.h>
#include <stdio.h>
#include <assert.h>
#include <inttypes.h>

#include <gxx/allocator.h>
#include <gxx/algorithm.h>
#include <gxx/utility.h>

#include <gxx/vector.h>

namespace gxx {
	template <class Allocator = gxx::allocator<char>>
	class basic_string {
	
		char* m_data;
		size_t m_capacity;
		size_t m_size;

		Allocator m_alloc;
	
	public:
		CONSTREF_GETTER(data, m_data);
		CONSTREF_GETTER(capacity, m_capacity);
		CONSTREF_GETTER(size, m_size);

		basic_string()  : m_data(nullptr), m_capacity(0), m_size(0) {}
	
		basic_string(const basic_string& other) : basic_string() {
			*this = other;
		}
	
		basic_string(basic_string&& other) : basic_string() {
			move(other);
		}
	
		basic_string(const char* str) : basic_string() {
			if (str) copy(str, strlen(str));
		}
	
		explicit basic_string(const char* str, size_t sz) : basic_string() {
			if (str) copy(str, sz);
		}

		~basic_string() {
			if (m_data) m_alloc.deallocate(m_data);
		};
	
	
		basic_string & copy(const char *cstr, size_t length) {
			if (!reserve(length)) {
				invalidate();
				return *this;
			}
			m_size = length;
			memcpy(m_data, cstr, length);
			return *this;
		}
	
	
		void move(basic_string &rhs) {
			if (m_data) m_alloc.deallocate(m_data);
			m_data = rhs.m_data;
			m_capacity = rhs.m_capacity;
			m_size = rhs.m_size;
			m_alloc = rhs.m_alloc;
			rhs.m_data = nullptr;
			rhs.m_capacity = 0;
			rhs.m_size = 0;
		}
	
	
		void invalidate(void) {
			if (m_data) m_alloc.deallocate(m_data);
			m_data = nullptr;
			m_capacity = m_size = 0;
		}
	
		basic_string & operator = (const basic_string &rhs) {
			if (this == &rhs) return *this;
			
			if (rhs.m_data) copy(rhs.m_data, rhs.m_size);
			else invalidate();
			
			return *this;
		}
		
		basic_string & operator = (basic_string &&rval) {
			if (this != &rval) move(rval);
			return *this;
		}

		basic_string & operator = (const char* str) {
			copy(str, strlen(str));
			return *this;
		}
	
		const char* c_str() {
			reserve(m_size + 1);
			*end() = 0;
			return begin();
		};
	
		char* begin() {
			return m_data;
		};
	
		char* end() {
			return m_data + m_size;		
		};
	
	
		unsigned char reserve(size_t sz) {
			if (m_data && m_capacity >= sz) return 1;
			if (changeBuffer(sz)) {
				return 1;
		}
		return 0;
		}
	
		unsigned char changeBuffer(size_t maxStrLen) {
			char *newbuf = (char *)m_alloc.reallocate(m_data, maxStrLen);
			if (newbuf) {
				m_data = newbuf;
				m_capacity = maxStrLen;
				return 1;
			}
			return 0;
		}
	
		unsigned char concat(const char *cstr, size_t length) {
			size_t newlen = m_size + length;
			if (!cstr) return 0;
			if (length == 0) return 1;
			if (!reserve(newlen)) return 0;
			memcpy(m_data + m_size, cstr, length);
			m_size = newlen;
			return 1;
		}
		
		unsigned char concat(char c) {
			return concat(&c, 1);
		}
	
		unsigned char concat(const char *cstr) {
			if (!cstr) return 0;
			return concat(cstr, strlen(cstr));
		}
	
		unsigned char concat(int8_t num, uint8_t base) {
			char buf[4];
			i8toa(num, buf, base);
			return concat(buf);
		}
	
		unsigned char concat(int16_t num, uint8_t base) {
			char buf[7];
			i16toa(num, buf, base);
			return concat(buf);
		}
	
		unsigned char concat(int32_t num, uint8_t base) {
			char buf[12];
			i32toa(num, buf, base);
			return concat(buf);
		}
	
		unsigned char concat(int64_t num, uint8_t base) {
			char buf[22];
			i64toa(num, buf, base);
			return concat(buf);
		}
	
		unsigned char concat(uint8_t num, uint8_t base) {
			char buf[4];
			u8toa(num, buf, base);
			return concat(buf);
		}
	
		unsigned char concat(uint16_t num, uint8_t base) {
			char buf[7];
			u16toa(num, buf, base);
			return concat(buf);
		}
	
		unsigned char concat(uint32_t num, uint8_t base) {
			char buf[12];
			u32toa(num, buf, base);
			return concat(buf);
		}
	
		unsigned char concat(uint64_t num, uint8_t base) {
			char buf[22];
			u64toa(num, buf, base);
			return concat(buf);
		}
	
		unsigned char concat(const basic_string& other) {
			return concat(other.data(), other.size());
		}
	
		basic_string number(uint8_t num, uint8_t base) {
			char buf[4];
			u8toa(num, buf, base);
			return gxx::move(basic_string(buf));
		};
	
		basic_string number(uint16_t num, uint8_t base) {
			char buf[7];
			u16toa(num, buf, base);
			return gxx::move(basic_string(buf));
		};
	
		basic_string number(uint32_t num, uint8_t base) {
			char buf[12];
			u32toa(num, buf, base);
			return gxx::move(basic_string(buf));
		};
		
		basic_string number(uint64_t num, uint8_t base) {
			char buf[22];
			u64toa(num, buf, base);
			return gxx::move(basic_string(buf));
		};
	
		basic_string number(int8_t num, uint8_t base) {
			char buf[4];
			i8toa(num, buf, base);
			return gxx::move(basic_string(buf));
		};
	
		basic_string number(int16_t num, uint8_t base) {
			char buf[7];
			i16toa(num, buf, base);
			return gxx::move(basic_string(buf));
		};
	
		basic_string number(int32_t num, uint8_t base) {
			char buf[12];
			i32toa(num, buf, base);
			return gxx::move(basic_string(buf));
		};
		
		basic_string number(int64_t num, uint8_t base) {
			char buf[22];
			i64toa(num, buf, base);
			return gxx::move(basic_string(buf));
		};
	
		basic_string number(double num, char format, uint8_t prec) {
			char buf[64];
			char fmt[] = "%.*x";
			fmt[3] = format;
			sprintf(buf, fmt, prec, num); 
			return basic_string(buf);
		};

		bool operator < (const basic_string& other) const {
			int ret = strncmp(data(), other.data(), gxx::min(size(), other.size()));
			if (ret == 0) return size() < other.size();
			else return ret < 0;
		};

		/*bool operator > (const basic_string& other) const {
			return other < *this;
		};*/

		bool operator == (const basic_string& other) const {
			return m_size == other.m_size ? strncmp(m_data, other.m_data, m_size) == 0 : false;
		};
	
		//basic_string hexdata(const void* data, size_t sz) {
		//	basic_string buf;
		//	buf.reserve(sz * 2 + 1);
		//	char* dst = buf.data();
		//	const uint8_t* src = (const uint8_t*) data;
		//	for (int i = 0; i < sz; i++) {
		//		byte2hex(dst, *src++);
		//		dst = dst + 2;
		//	}
		//};
	
		basic_string format(const char* fmt, ...) {
			char buf[128];
	
			va_list args;
			//assert(format != NULL);
			va_start(args, format);
			vsprintf(buf, fmt, args); 
			va_end(args);
	
			return gxx::move(basic_string(buf));
		};
	
		/*static basic_string number(uint16_t num, uint8_t base = 10);
		static basic_string number(uint32_t num, uint8_t base = 10);
		static basic_string number(uint64_t num, uint8_t base = 10);
			
		static basic_string number(int8_t num, uint8_t base = 10);
		static basic_string number(int16_t num, uint8_t base = 10);
		static basic_string number(int32_t num, uint8_t base = 10);
		static basic_string number(int64_t num, uint8_t base = 10);
	*/
	
		basic_string & shrink() {
			changeBuffer(m_size);
			return *this;
		}
	
		basic_string & shrink_to_print() {
			changeBuffer(m_size + 1);
			return *this;
		}
		

		basic_string& resize(size_t sz) {
			reserve(sz);
			assert(sz <= m_capacity);
			m_size = sz;
			return *this;
		}

		void swap(basic_string& other) {
			gxx::swap(m_data, other.m_data);
			gxx::swap(m_size, other.m_size);
			gxx::swap(m_capacity, other.m_capacity);
		}

		gxx::vector<basic_string> split(char delim) {
			gxx::vector<basic_string> outvec;

			char* strt;
			char* ptr = data();
			char* end = data() + size();
			
			while(true) {
				strt = ptr;

				while (*ptr != delim && ptr != end) ptr++;
				outvec.emplace_back(strt, ptr - strt);		

				if (*ptr == delim) ptr++;
				else break;
			}

			return outvec;
		}

		/*size_t size() const {
			return m_size;
		}; 
	
		size_t capacity() const {
			return m_capacity;
		};
	
		char* data() const {
			return m_data;
		};*/
	
	/*basic_string & copy(const __FlashStringHelper *pstr, unsigned int length)
	{
		if (!reserve(length)) {
			invalidate();
			return *this;
		}
		len = length;
		strcpy_P(buffer, (PGM_P)pstr);
		return *this;
	}*/
	/*

basic_string & operator = (StringSumHelper &&rval)
{
	if (this != &rval) move(rval);
	return *this;
}

basic_string & operator = (const char *cstr)
{
	if (cstr) copy(cstr, strlen(cstr));
	else invalidate();
	
	return *this;
}

basic_string & operator = (const gxx::buffer& cptr)
{
	if (cptr.data()) copy((const char*)cptr.data(), cptr.size());
	else invalidate();
	
	return *this;
}

*/



/*
	~basic_string() {
		release();
	}	

	void release() {
		m_record->refs--;
		if (m_record->refs <= 0) {
			if (m_record->data) m_alloc->deallocate(m_record->data);
			m_alloc->destructObject(m_record);
		}
	}

	uint8_t reserve(size_t sz) {
		if (capacity() >= sz) return 1;
		return changeBuffer(sz);
	}

	uint8_t changeBuffer(size_t sz) {
		char* oldbuf = m_record->data;
		char* newbuf = (char*)m_alloc->allocate(sz);
		if (!oldbuf) memcpy(newbuf, oldbuf, m_record->size);
		m_record->capacity = sz;
		m_record->data = newbuf;	
		if (oldbuf) m_alloc->deallocate(oldbuf);
		return 1;
	}

	size_t size() const {
		return m_record->size;
	};

	size_t capacity() const {
		return m_record->capacity;
	};


	char* data() {
		return m_record->data;
	};

	basic_string& operator= (const basic_string& other) {
		release();
		m_record = other.m_record;
		m_record->refs++;		
	}
*/
	};

	using string = basic_string<>;	

	namespace string_literal {
		static string operator"" _gs (const char* name, size_t sz) { return string(name, sz); }
	}

	using strvec = gxx::vector<gxx::string>;

	gxx::strvec split(gxx::string str, char delim);
}

#endif