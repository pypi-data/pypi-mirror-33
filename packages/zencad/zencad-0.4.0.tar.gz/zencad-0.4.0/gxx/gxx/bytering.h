#ifndef UTILXX_BYTE_RING_H
#define UTILXX_BYTE_RING_H

#include <stdlib.h>
#include <gxx/buffer.h>
#include <gxx/panic.h>

namespace gxx {

	class bytering {
		gxx::buffer m_buf;
	
		size_t head;
		size_t tail;
	
		inline void fixup(size_t& ref) {
			while (ref >= m_buf.size()) ref -= m_buf.size(); 
		}
	
	public:
		//bytering(){};
	
		bytering(char* buf, size_t sz) : m_buf(buf,sz), head(0), tail(0) {};
		bytering(gxx::buffer buf) : m_buf(buf), head(0), tail(0) {};
	
		void init(char* buffer, size_t size) {
			m_buf.data(buffer);
			m_buf.size(size);
			head = tail = 0;
		}
	
		bool empty() volatile {
			return head == tail;
		}
	
		int clean() {
			head = tail = 0;	
		}

		bool full() {
			return head == (tail ? tail : m_buf.size()) - 1;
		}
	
		int push(char c) {
			if (full()) return 0;
			*(m_buf.data() + head++) = c;
			fixup(head);
			return 1;
		}
		
		int push(const char* data, size_t size) {
			int ret = 0;
			while(size--) {
				if(!push(*data++)) {
					return ret;
				};
				ret++;
			}
			return ret;
		}
	
		int pop() {
			//dprln(tail);
			if (empty()) return -1;
			char c = *(m_buf.data() + tail++);
			fixup(tail);
			return c;
		}
	
		int popn(char* data, size_t size) {
			int ret = 0;
			while(size--) {
				int r = pop();
				if (r == -1) {
					return ret;
				}
				*data++ = r;
				ret++;
			}
			return ret;
		}

		int pick() {
			gxx::panic("NeedToImplement");
		}

		int pickn(char* data, size_t size) {
			int e = tail + size;
			
			if (e < m_buf.size()) {
				memcpy(data, m_buf.data() + tail, size);
			} else {
				e = e % m_buf.size();
				memcpy(m_buf.data() + tail, data, e);
				memcpy(m_buf.data(), data, size - e);	
			}
			return size;
		}

		gxx::buffer first_part_as_buffer() {
			return gxx::buffer(m_buf.data() + tail, head >= tail ? head - tail : m_buf.size() - tail);
		}
	
		gxx::buffer last_part_as_buffer() {
			return gxx::buffer(m_buf.data(), head >= tail ? 0 : tail);
		}

		size_t avail() { 
			return (head >= tail) ? head - tail : m_buf.size() + head - tail; 
		};
	
		size_t room() {
			return (head >= tail) ? m_buf.size() - 1 + ( tail - head ) : ( tail - head ) - 1;
		};
	
		//size_t size() {
		//	return m_buf.size();
		//};
	};
}

#endif