#ifndef GXX_READLINE_READLINE_H
#define GXX_READLINE_READLINE_H

namespace gxx {
	class line {
		char* buf;
		size_t capacity;
		size_t cursor;
		size_t size;

		void left(int n) 	{ cursor = 	n > cursor 			? 0 	: cursor - n; };
		void right(int n) 	{ cursor = 	cursor + n > size 	? size 	: size; };

		void putchar(char c) {
			if (size == capacity) return;

			if (cursor != size) {
				memmove(buf + cursor + 1, buf + cursor, size - cursor);
			}

			buf[cursor++] = c;
			size++;
		}

		size_t postfix() {
			return size - cursor;
		}

		gxx::buffer postfix_buffer() {
			return gxx::buffer(buf + cursor, size - cursor);
		}
	};

	class readline {
		gxx::line line;

		uint8_t state = 0;
		gxx::terminal_controller echo;

	public:
		readline(gxx::buffer line, gxx::io:ostream* echo) : line(buf), echo(echo) {}

		void putchar(char c) {
			switch (state) {
				case 0: 
					switch(char c) {
						case 0x1B:
							state = 1;
						default:
							line.putchar(c);
							if (echo) {
								echo.putchar(c);
								if (line.postfix() != 0) {
									term.write(line.postfix_buffer());
									term.left(line.postfix());
								}
							}
					}
			}
		}
	};
}

#endif