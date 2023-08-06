#ifndef GXX_LINUX_EPOLL_H
#define GXX_LINUX_EPOLL_H

#include <sys/epoll.h>

namespace gxx {
	class epoll {
		int efd;

	public:
		int create() {
			efd = epoll_create(10);
			if (efd == -1) {
				perror ("epoll_ctl");
				abort ();
			}
		}

		int add(int fd) {
			struct epoll_event event;
  			event.data.fd = fd;
			event.events = EPOLLIN | EPOLLERR | EPOLLET;

			int s = epoll_ctl (efd, EPOLL_CTL_ADD, fd, &event);
			if (s == -1) {
				perror ("epoll_ctl");
				abort ();
			}
		}

		struct epoll_event wait() {
			struct epoll_event event;
			int s = epoll_wait (efd, &event, 1, -1);
			if (s == -1) {
				perror ("epoll_ctl");
				abort ();
			}

			return event;
		}
	};
}

#endif