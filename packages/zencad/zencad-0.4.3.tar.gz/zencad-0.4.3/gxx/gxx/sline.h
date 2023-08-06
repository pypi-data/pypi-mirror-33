#ifndef GXX_SLINE_H
#define GXX_SLINE_H

#include <gxx/buffer.h>

namespace gxx {
	class sline {
		char* data;
		size_t capacity;
		size_t cursor;

	public:
		sline(gxx::buffer buf) : data(buf.data()), capacity(buf.size()), cursor(0) {}
		sline(){}

		void back(int n) {
			cursor -= n;
		}

		void init() {
			cursor = 0;
		}

		void init(gxx::buffer buf) {
			data = buf.data();
			capacity = buf.size();
			cursor = 0;
		}

		int size() {
			return cursor;
		}

		int avail() {
			return capacity - cursor;
		}

		int putchar(char c) {
			*(data + cursor) = c;
			cursor++;
		}

		int write(const char* dat, size_t sz) {
			size_t av = avail();
			size_t len = sz < av ? sz : av;

			memcpy(data + cursor, dat, len);
			cursor += len;
		}

		operator gxx::buffer() {
			return gxx::buffer(data, cursor);
		}
	};
}

#endif