#ifndef GENOS_UTILXX_BUFFER_H
#define GENOS_UTILXX_BUFFER_H

//#include <string>
#include <string.h>
#include <stdlib.h>

#include <gxx/util/setget.h>

namespace gxx {
	class buffer {
	protected:
		char* buf;
		size_t sz;
	public:
		buffer() : buf(nullptr), sz(0) {}
		//buffer(const char* buf) : buf((char*)buf), sz(strlen(buf)) {}
		buffer(const void* _buf, size_t _sz) : buf((char*)_buf), sz(_sz) {}
		//buffer(const std::string& str) : buf((char*)str.data()), sz(str.size()) {}

        template<size_t N> inline buffer(const char (&arr) [N]) : buf((char*)arr), sz(N) {}

		//bool empty() { return buf == nullptr; }

		bool operator==(const buffer& other) const {
			return (sz == other.sz) && (strncmp(buf, other.buf, sz < other.sz ? sz : other.sz) == 0);
		}

		bool operator!=(const buffer& other) const {
			return (sz != other.sz) || (strncmp(buf, other.buf, sz < other.sz ? sz : other.sz) != 0);
		}

		bool operator==(const char* str) {
			return strncmp(buf, str, sz) == 0;
		}

		bool operator!=(const char* str) {
			return strncmp(buf, str, sz) != 0;
		}

		char& operator[](size_t num) {
			return *(buf + num);
		}

		char operator[](size_t num) const {
			return *(buf + num);
		}

		ACCESSOR(data, buf);
		ACCESSOR(size, sz);

        char* begin() { return buf; }
        char* end() { return buf + sz; }

		bool empty() {
			return buf == nullptr;
		}

		buffer slice(size_t idx, size_t _sz) {
			return buffer(buf + idx, _sz);
		}

		//static gxx::buffer(int)

		/*static gxx::buffer from_string(const std::string& str) {
			return gxx::buffer(str.data(), str.size());
		}
		static gxx::buffer on_string(const std::string& str) {
			return gxx::buffer(str.data(), str.size());
		}*/

		template<typename T>
		static gxx::buffer on_object(T& obj) {
			return gxx::buffer((char*)&obj, sizeof(obj));
		}
	};

	static inline gxx::buffer allocate_buffer(int sz) {
		void* ptr = malloc(sz);
		return gxx::buffer(ptr, sz);
	}

	namespace buffer_literal {
		inline gxx::buffer operator"" _b(const char* str, size_t sz) { return gxx::buffer(str, sz); }
	}

	class smart_buffer : public buffer {
	public:
		smart_buffer(size_t n) : buffer(allocate_buffer(n)) {}

		smart_buffer(const char* d, size_t n) : buffer(allocate_buffer(n)) {
			memcpy(buf, d, n);
		}

		~smart_buffer() {
			free(buf);
		}
	};
}

#endif
