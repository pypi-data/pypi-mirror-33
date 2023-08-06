#ifndef GXX_HISTORY_H
#define GXX_HISTORY_H

#include <string>
#include <gxx/ring.h>
#include <gxx/buffer.h>

namespace gxx {
	class history {
	public:
		gxx::ring<gxx::smart_buffer> hist;

	public:
		history() : hist() {}

		void init(int len) {
			hist.reserve(len);
		}

		void push_string(const char* data, size_t size) {
			if (size == 0) return;
			if (hist.size() == hist.capacity()) hist.pop();
			hist.emplace(data, size);
		}			

		void push_string(const char* data) {
			push_string(data, strlen(data));
		}

		void push_string(gxx::buffer data) {
			push_string(data.data(), data.size());
		}

		const gxx::smart_buffer& operator[](int i) {
			return hist[i];
		}

		size_t size() {
			return hist.size();
		}
	};
}

#endif