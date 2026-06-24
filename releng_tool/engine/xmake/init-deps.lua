-- SPDX-License-Identifier: BSD-2-Clause
-- Copyright releng-tool
--
-- Script helps provide the full path for xmake target dependency paths. It
-- has been observed on OSX that xmake can fail building some libraries due
-- to issues that target dependency folders do not exist. What this script
-- provides is a list of target paths that can be used for a build. releng-tool
-- can then pre-make these paths to help workaround the issue. Note that this
-- issue has not been observed on Linux/Windows. Observed on 
--
-- Issue relates to xmake's `depend.save`, which tries to save a dependency
-- into a non-existent path (xmake/modules/private/action/build/object.lua).
--
-- Issue at the time of writing was observed on:
--
--  $ system_profiler SPHardwareDataType | grep "Model Identifier"
--  Model Identifier: Macmini6,1
--  $ xmake --version
--  xmake v3.0.9+20260621, A cross-platform build utility based on Lua
--
-- Also observed in GitHub actions running `macos-latest`:
-- https://github.com/releng-tool/releng-tool/actions/runs/27911847076/job/82590214339

function main()
    import("core.project.project")
    import("core.project.config")

    config.load()

    local plat = config.get("plat") or os.host()
    local arch = config.get("arch") or os.arch()
    local mode = config.get("mode") or "release"

    for name, _ in pairs(project.targets()) do
        print(path.join(name, plat, arch, mode))
    end

    return ""
end
