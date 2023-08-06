#ifndef GXX_OSUTIL_SIGNAL_H
#define GXX_OSUTIL_SIGNAL_H

namespace gxx {
	namespace osutil {
		void setsig(int fd, int sig);
   		void signal(int sig, void(*handler)(int));
	}
}

#endif