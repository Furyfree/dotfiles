-- Workspace defaults, monitor assignments, and special workspaces.

-- Keep numbered workspaces available even when empty, including in Noctalia.
for workspace = 1, 10 do
    hl.workspace_rule({ workspace = tostring(workspace), persistent = true })
end

-- Assign workspaces to monitors once both monitor setups are known.
