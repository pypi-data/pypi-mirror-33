#ifndef GXX_READLINE_TERMDISP_H
#define GXX_READLINE_TERMDISP_H

#include <gxx/io/ostream.h>

namespace gxx {
	class termdisp {
		virtual void putchar(char c);
		virtual void up(int n);
		virtual void down(int n);	
		virtual void right(int n);
		virtual void left(int n);
		virtual void backspace();
	};
	
	class termdisp_vt100 : public termdisp {
	public:
		gxx::io::ostream& out;
	
		termdisp_vt100(gxx::io::ostream& out) : out(out) {}
	
		void putchar(char c) override {
			out.putchar(c);
		}
	
		void __move(char com, int n) {
			out.putchar(0x1B);
			out.putchar('[');
			out.print(n);
			out.putchar(com);			
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
	
		void backspace() override {	
			left(1);
			del();
		}

		void del() {
			out.putchar(' ');
			left(1);
		} 
	};
}

#endif