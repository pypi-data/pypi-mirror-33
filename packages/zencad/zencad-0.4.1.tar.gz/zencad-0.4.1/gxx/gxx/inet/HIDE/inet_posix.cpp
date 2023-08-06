#include <gxx/inet/hostaddr.h>
#include <unistd.h>

gxx::inet::netaddr::netaddr(unsigned long addr, unsigned short port) 
	: addr(addr), port(port) {}
