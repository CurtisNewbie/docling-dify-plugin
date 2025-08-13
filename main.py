from dify_plugin import Plugin, DifyPluginEnv

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=60 * 15))

if __name__ == '__main__':
    plugin.run()
