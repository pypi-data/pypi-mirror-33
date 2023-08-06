#ifndef GXX_READLINE_TERMDISP_H
#define GXX_READLINE_TERMDISP_H

#include <gxx/io/ostream.h>

namespace gxx {
	class termdisp : public gxx::io::ostream {
		gxx::io::ostream& out;
	public:
		termdisp(gxx::io::ostream& out) : out(out) {}

		virtual void up(int n) = 0;
		virtual void down(int n) = 0;	
		virtual void right(int n) = 0;
		virtual void left(int n) = 0;
		virtual void backspace(int n) = 0;

	protected:
		int writeData(const char* data, size_t size) {
			out.write(data, size);
		}
	};
	
	class termdisp_vt100 : public termdisp {
	public:
		
		termdisp_vt100(gxx::io::ostream& out) : termdisp(out) {}
		void __move(char com, int n) {
			if (n == 0) return;
			putchar(0x1B);
			putchar('[');
			print(n);
			putchar(com);			
		}

		void up(int n) override {
			__move('A', n);
		}
	
		void down(int n) override {
			__move('B', n);
		}
	
		void right(int n) override {
			__move('C', n);	
		}
	
		void left(int n) override {
			__move('D', n);	
		}
	
		void backspace(int n) override {	
			if (n == 0) return;
			left(1);
			del();
		}

		void del() {
			putchar(' ');
			left(1);
		} 
	};
}

#endif