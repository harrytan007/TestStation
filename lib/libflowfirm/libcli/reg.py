#coding=utf-8

def regist(node):
    """注册CLI资源"""
    if node.tag == "flowfirm_cli":
        if node.findtext("type") == "G":
            import cli_g
            return cli_g.CliG(node)
        elif node.findtext("type") == "D":
            import cli_d
            return cil_d.CliD(node)
