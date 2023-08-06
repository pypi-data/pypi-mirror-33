#ifndef GXX_TERMINAL_H
#define GXX_TERMINAL_H

#include <gxx/io/iostream.h>
#include <gxx/panic.h>
#include <gxx/line.h>
#include <gxx/terminal/termdisp.h>
#include <gxx/terminal/history.h>

namespace gxx {
	class terminal_core {
		gxx::termdisp_vt100 disp;
		gxx::history hist;
		gxx::line line;

		int8_t hindex = 0;
	public:
		gxx::delegate<void, gxx::buffer> line_handler;

	public:
		terminal_core(gxx::io::ostream & out, gxx::buffer buf) : disp(out), hist(), line(buf) {}

		uint8_t state = 0;
		uint8_t echo = true;

		int arg = 0;

		void init() {
			hist.init(10);
		}

		void newline() {
			disp.println();

			if(line.size() != 0) {
				line_handler(line);
				hist.push_string(line);
				line.clean();
			}

			hindex = 0;
			start();
		}

		void start() {
			disp.print("> ");
		}

		void left(int n) { if (n == 0) return; disp.left(line.left(n)); }
		
		void right(int n) { if (n == 0) return; disp.right(line.right(n)); }

		void clean() {
			disp.left(line.prefix());
			size_t sz = line.size();
			disp.fill(' ', sz);
			disp.left(sz);	
		}
		
		void up() { 
			if (hist.size() == hindex) return;
			clean();
			line = hist[-(++hindex)];
			disp.print(line);
		}

		void down() { 
			if (hindex != 0) --hindex;
			if (hindex == 0) {
				clean();
				line.clean();	
				return;
			}
			clean();
			line = hist[-(hindex)];
			disp.print(line);

		}

		void newchar(char c) {
			switch (state) {
				case 0: 
					switch(c) {
						case '\n': 
							return;
						case '\r': 
							newline();
							return;
						case '\b':
							disp.backspace(line.backspace(1));
							return;
						case 0x1B:
							state = 1;
							return;						
						default:
							line.putchar(c);
							int postfix = line.postfix();
							if (postfix == 0) disp.putchar(c);
							else {
								disp.print(line.postfix_buffer());
								left(postfix);
							}
							return;
					}
				case 1:
					if (c == '[') {
						arg = 0;
						state = 2;
					}
					else state = 0;
					break;
				case 2:
					if (isdigit(c)) { 
						arg = arg * 10 + (c - '0');
						return;
					}
					switch (c) {
						case 'A' : up(); break;
						case 'B' : down(); break;
						case 'C' : right(1); break;
						case 'D' : left(1); break;
					}
					state = 0;
					break;

				default:
					gxx::panic("terminal, default state");
			}
		}
	};
}

#endif