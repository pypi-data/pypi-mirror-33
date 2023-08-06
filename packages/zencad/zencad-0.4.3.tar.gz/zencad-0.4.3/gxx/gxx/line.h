#ifndef GXX_LINE_H
#define GXX_LINE_H

#include <gxx/buffer.h>

namespace gxx {
	class line {
		char* buffer;
		size_t capacity;
		size_t sz;
		size_t cursor;

	public:
		line(gxx::buffer buf) : buffer(buf.data()), capacity(buf.size()), sz(0), cursor(0) {}

		void clean() {
			cursor = sz = 0;
		}

		int putchar(char c) {
			if (sz == capacity) return 0;
			if (cursor == sz) {
				*(buffer + cursor) = c;
				++cursor;
				++sz; 
				return 1;
			}
		}
		
		int backspace(int n) {
			if (cursor == 0) return 0;
			if (cursor == sz) {
				--cursor;
				--sz;
				return 1;
			}
		}

		int left(uint8_t n) {
			return n;
		} 

		int right(uint8_t n) {
			return n;			
		} 

		int prefix() {
			return cursor;
		}

		int postfix() {
			return sz - cursor;
		}

		int size() {
			return sz;
		}

		gxx::buffer postfix_buffer() {
			return gxx::buffer();
		}

		void operator= (gxx::buffer arr) {
			memcpy(buffer, arr.data(), arr.size());
			cursor = sz = arr.size();
		}

		operator gxx::buffer() {
			return gxx::buffer(buffer, sz);
		}
	};
}

#endif