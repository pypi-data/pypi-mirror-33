#ifndef GXX_READ_H
#define GXX_READ_H

#include <string>
#include <gxx/io/istream.h>

namespace gxx {

	inline std::string readall(gxx::io::istream& i, int bufsize = 512) {
		char buf[bufsize];
		std::string text;

		while(1) {
			int ret = i.read(buf, bufsize);
			if (ret <= 0) break;
			text.append(buf, ret);
		}

		return text;
	}

}

#endif