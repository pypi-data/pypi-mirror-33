env_conf = [
    {
        "env": "dev-wc",
        "url": "http://172.16.101.142:9090"
    },
    {
        "env": "dev-hollywood",
        "url": "http://172.16.101.137:9090"
    },
    {
        "env": "dev-guanhua",
        "url": "http://172.16.101.138:9090"
    },
    {
        "env": "dev-dragon",
        "url": "http://172.16.101.132:9090"
    },
    {
        "env": "dev-qingsong",
        "url": "http://172.16.101.46:9090"
    },
    {
        "env": "dev-hecate",
        "url": "http://172.16.101.144:9090"
    },
    {
        "env": "dev-helion",
        "url": "http://172.16.101.5:9090"
    },
    {
        "env": "dev-budget",
        "url": "http://172.16.101.65:9090"
    },
    {
        "env": "dev-photon",
        "url": "http://172.16.101.97:9090"
    },
    {
        "env": "dev-bfront",
        "url": "http://172.16.101.103:9090"
    },
    {
        "env": "dev-metadata",
        "url": "http://172.16.101.106:9090"
    },
    {
        "env": "dev-dh",
        "url": "http://172.16.103.241:9090"
    },
    {
        "env": "test1",
        "url": "http://172.16.101.50:9090"
    },
    {
        "env": "test3",
        "url": "http://172.16.101.47:9090"
    },
    {
        "env": "test7",
        "url": "http://172.16.101.131:9090"
    },
    {
        "env": "test8",
        "url": "http://172.16.101.76:9090"
    },
    {
        "env": "test9",
        "url": "http://172.16.101.50:9090"
    },
    {
        "env": "test-experts",
        "url": "http://172.16.101.84:9090"
    },
    {
        "env": "test-finance",
        "url": "http://172.16.101.79:9090"
    },
    {
        "env": "test-search",
        "url": "http://172.16.101.53:9090"
    },
    {
        "env": "test-plansearch",
        "url": "http://172.16.101.88:9090"
    },
    {
        "env": "test-pressure",
        "url": "http://172.16.101.149:9090"
    },
    {
        "env": "test-purchaseplan",
        "url": "http://172.16.101.40:9090"
    },
    {
        "env": "test-workflow",
        "url": "http://172.16.101.71:9090"
    },
    {
        "env": "staging",
        "url": "http://172.31.2.179:8181"
    },
    {
        "env": "prod",
        "url": "http://172.20.12.241:9090"
    }
]


def get_available_env():
    envs = map(lambda x: x.get('env'), env_conf)
    envs.sort(key=lambda x: x)
    return ', '.join(envs)
