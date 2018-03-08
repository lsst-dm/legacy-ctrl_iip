#include <stdint.h>

extern "C" {
  uint32_t  getCommitHash();
  int       isDirty();
  char      *getReleaseTag();
  double    getReleaseTime();
};

