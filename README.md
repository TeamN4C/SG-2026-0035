# Node2Shell

This project reproduces CVE-2026-111497 in the default `node:24.22.0` environment. The target and exploit are designed for Linux x86_64.

## Requirements

- Linux x86_64
- Docker Engine
- Python 3
- Available TCP ports `31338` and `4453`

Leave `UV_THREADPOOL_SIZE` unset to use the default four libuv workers.

## Set Up the Target Environment

Run the following commands in the first terminal:

```sh
cd SG-2026-0035
./run-docker.sh
```

```text
listening on http://127.0.0.1:31338
```

## Run the Exploit

Run the exploit without arguments in the second terminal:

```sh
cd SG-2026-0035
python3 exploit.py
```

On success, a reverse shell connects after the following messages:

```text
[*] groom
[*] trigger
[+] shell
```

Verify the privileges from the connected shell:

```sh
id
```

Each invocation sends seven warm-up requests followed by one malicious request over the same TCP connection. `exploit.py` performs no reconnection or automatic retry.

## Observed Success Rate

The measurement used the same host-network environment as `run-docker.sh`. Each trial started with a fresh container and executed the current `exploit.py` exactly once. A trial was counted as successful when the reverse-shell callback connected and `id` returned `uid=0(root)`.

- Successful trials: 5
- Total trials: 20
- Observed success rate: approximately 25%
- Infrastructure failures: 0
