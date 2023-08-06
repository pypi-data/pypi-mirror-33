#ifndef GXX_READLINE_H
#define GXX_READLINE_H

#include <gxx/event/multiple_delegate.h>
#include <gxx/util/setget.h>
#include <gxx/buffer.h>
#include <stdlib.h>

namespace gxx {
	class simple_readline {
		char* m_data;
		char* m_data_end;
		char* m_cursor;
		char lastsymb;

		gxx::delegate<void, const char*, size_t> m_line_handler;
		gxx::delegate<int, simple_readline&> m_full_handler;
	public:
		void reset() {
			m_cursor = m_data;
			lastsymb = 0;
		}

		bool is_full() {
			return m_cursor == m_data_end;
		}

	public:
		SETTER(set_line_handler, m_line_handler);
		SETTER(set_full_handler, m_full_handler);

		simple_readline(gxx::buffer buf) : m_data(buf.data()), m_data_end(buf.data() + buf.size() - 1), m_cursor(buf.data()) {}

		int write(const char* str, size_t sz) {
			char* readptr = (char*) str;			
			while(sz--) {
				//dprln("iter");
				while (is_full()) { 
					int ret = m_full_handler(*this);
					if (ret == -1) return -1;
				} 
				
				char c = *readptr++;

				if (c == '\n') {
					*m_cursor = 0;
					if (lastsymb == '\r') *(m_cursor - 1) = 0;
					m_line_handler(m_data, m_cursor - m_data);
					//dprln("here");
					reset();
					continue;
				} 
				
				*m_cursor++ = c;
				lastsymb = c;
			}
		}

		size_t size() const {
			return m_cursor - m_data;
		}

		const char* data() const {
			return m_data;
		}

		char* line() {
			*m_cursor = 0;
			return m_data;
		}

		gxx::buffer to_buffer() {
			return gxx::buffer(m_data, size());
		}
	};
}

#endif
