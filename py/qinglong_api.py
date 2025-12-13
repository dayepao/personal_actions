import os
import time

from utils_dayepao import http_request


class qinglong:
    def __init__(self, url, client_id, client_secret):
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()

    def get_token(self):
        url = f"{self.url}/open/auth/token?client_id={self.client_id}&client_secret={self.client_secret}"
        res = http_request("get", url)
        if res.json().get("code") != 200:
            raise Exception("无法获取用户密钥，请检查 client_id 和 client_secret 是否正确")
        return res.json().get("data").get("token")

    def get_envs(self):
        url = f"{self.url}/open/envs?t={time.time()}"
        headers = {"Authorization": f"Bearer {self.token}"}
        res = http_request("get", url, headers=headers)
        if res.json().get("code") != 200:
            raise Exception("无法获取环境变量，请检查 token 是否正确")
        return res.json().get("data")

    def get_env_ids(self, names: list):
        # 对输入进行处理，确保 name 是列表
        names = [names] if not isinstance(names, list) else names
        envs = self.get_envs()
        env_ids = []
        for name in names:
            for env in envs:
                if env.get("name") == name:
                    env_ids.append(env.get("id"))
                    break
            else:
                print(f"环境变量 {name} 不存在")
                env_ids.append(None)
        return env_ids

    def add_envs(self, names: list, values: list, remarks: list = []):
        # 对输入进行处理，确保它们都是列表
        names, values = map(lambda x: [x] if not isinstance(x, list) else x, [names, values])

        # 当remarks为None或[]或""时，自动将remarks填充空值到names的长度
        if remarks is None or remarks == [] or remarks == "":
            remarks = [""] * len(names)
        else:
            remarks = [remarks] if not isinstance(remarks, list) else remarks

        # 检查 names, values, remarks 的长度是否相等
        if len(names) != len(values) or len(names) != len(remarks):
            raise ValueError("names, values 和 remarks 的长度必须相等")

        for name in names:
            if name in [env.get("name") for env in self.get_envs()]:
                raise Exception(f"环境变量 {name} 已存在")
        url = f"{self.url}/open/envs?t={time.time()}"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = []
        for name, value, remark in zip(names, values, remarks):
            data.append({"name": name, "value": value, "remarks": remark})
        res = http_request("post", url, headers=headers, json=data)
        if res.json().get("code") != 200:
            raise Exception("无法添加环境变量，请检查 token 是否正确")
        return res.json().get("data")

    def update_env(self, name: str, value: str, remark: str = ""):
        # 对输入进行处理，确保它们都是字符串
        name, value, remark = map(lambda x: str(x) if not isinstance(x, str) else x, [name, value, remark])

        # 获取环境变量 id
        env_id = self.get_env_ids(name)[0]

        if env_id is None:
            print(f"环境变量 {name} 不存在，将自动创建")
            return self.add_envs(name, value, remark)

        # 更新环境变量
        url = f"{self.url}/open/envs?t={time.time()}"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"name": name, "value": value, "remarks": remark, "id": env_id}
        res = http_request("put", url, headers=headers, json=data)
        if res.json().get("code") != 200:
            raise Exception("无法更新环境变量，请检查 token 是否正确")
        return res.json().get("data")

    def delete_env(self, names: list):
        # 对输入进行处理，确保 name 是列表
        names = [names] if not isinstance(names, list) else names

        # 获取环境变量 id
        env_ids = self.get_env_ids(names)

        url = f"{self.url}/open/envs?t={time.time()}"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = []
        for env_id in env_ids:
            if env_id is None:
                continue
            data.append(env_id)
        # 删除环境变量
        if data == []:
            print("没有环境变量需要删除")
            return None
        res = http_request("request", url, headers=headers, json=data, method="DELETE")
        if res.json().get("code") != 200:
            raise Exception("无法删除环境变量，请检查 token 是否正确")
        return res.json().get("data")


if __name__ == "__main__":
    qinglong_url = os.getenv("QL_PANEL_URL")
    qinglong_client_id = os.getenv("QL_CLIENT_ID")
    qinglong_client_secret = os.getenv("QL_CLIENT_SECRET")
    ql = qinglong(qinglong_url, qinglong_client_id, qinglong_client_secret)
    # ql.add_envs(["TEST_ENV1", "TEST_ENV2"], ["test1", "test2"], ["备注1", "备注2"])
    print(ql.delete_env(["TEST_ENV1", "TEST_ENV2"]))
    print(ql.get_envs())
