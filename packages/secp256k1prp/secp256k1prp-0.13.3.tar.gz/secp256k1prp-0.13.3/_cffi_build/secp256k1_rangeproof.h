void secp256k1_pedersen_context_initialize(secp256k1_context* ctx);

int secp256k1_pedersen_commit(
  const secp256k1_context* ctx,
  unsigned char *commit,
  unsigned char *blind,
  uint64_t value
);

int secp256k1_pedersen_blind_sum(
  const secp256k1_context* ctx,
  unsigned char *blind_out,
  const unsigned char * const *blinds,
  int n,
  int npositive
);

int secp256k1_pedersen_verify_tally(
  const secp256k1_context* ctx,
  const unsigned char * const *commits,
  int pcnt,
  const unsigned char * const *ncommits,
  int ncnt,
  int64_t excess
);

void secp256k1_rangeproof_context_initialize(secp256k1_context* ctx);

int secp256k1_rangeproof_verify(
  const secp256k1_context* ctx,
  uint64_t *min_value,
  uint64_t *max_value,
  const unsigned char *commit,
  const unsigned char *proof,
  int plen
);

int secp256k1_rangeproof_rewind(
  const secp256k1_context* ctx,
  unsigned char *blind_out,
  uint64_t *value_out,
  unsigned char *message_out,
  int *outlen,
  const unsigned char *nonce,
  uint64_t *min_value,
  uint64_t *max_value,
  const unsigned char *commit,
  const unsigned char *proof,
  int plen
);

int secp256k1_rangeproof_sign(
  const secp256k1_context* ctx,
  unsigned char *proof,
  int *plen,
  uint64_t min_value,
  const unsigned char *commit,
  const unsigned char *blind,
  const unsigned char *nonce,
  int exp,
  int min_bits,
  uint64_t value
);

int secp256k1_rangeproof_info(
  const secp256k1_context* ctx,
  int *exp,
  int *mantissa,
  uint64_t *min_value,
  uint64_t *max_value,
  const unsigned char *proof,
  int plen
);

