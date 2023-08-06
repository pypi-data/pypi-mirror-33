#ifndef GXX_STDSTRM_H
#define GXX_STDSTRM_H

#include <gxx/io/fdfile.h>
#include <unistd.h>

namespace gxx {
	extern io::fdfile cin;
	extern io::fdfile cout;
	extern io::fdfile cerr;
}

#endif