#include <gxx/log/logger.h>
#include <string.h>

#include <mutex>

static std::mutex tsmutex;
void gxx::log::standart_logger_timestamp(char * str, size_t maxlen) {
	std::lock_guard<std::mutex> lock(tsmutex);
	std::time_t result = std::time(NULL);
	strcpy(str, std::asctime(std::localtime(&result)));
	str[strlen(str) - 1] = 0;
}
