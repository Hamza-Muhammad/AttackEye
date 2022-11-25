-- Copyright 2017-2021 Jeff Foley. All rights reserved.
-- Use of this source code is governed by Apache 2 LICENSE that can be found in the LICENSE file.

local json = require("json")

name = "FacebookCT"
type = "cert"
api_version = "v11.0"

function start()
    set_rate_limit(5)
end

function check()
    local c
    local cfg = datasrc_config()
    if cfg ~= nil then
        c = cfg.credentials
    end

    if (c ~= nil and c.key ~= nil and 
        c.secret ~= nil and c.key ~= "" and c.secret ~= "") then
        return true
    end
    return false
end

function vertical(ctx, domain)
    local nxt = query_url(domain, get_token(ctx))

    while nxt ~= "" do
        resp, err = request(ctx, {['url']=nxt})
        if (err ~= nil and err ~= "") then
            log(ctx, "vertical request to service failed: " .. err)
            return
        end

        dec = json.decode(resp)
        if (dec == nil or dec.data == nil or #(dec.data) == 0) then
            return
        end

        for _, r in pairs(dec.data) do
            for _, name in pairs(r.domains) do
                new_name(ctx, name)
            end
        end

        nxt = ""
        if (dec.paging ~= nil and dec.paging.next ~= nil and dec.paging.next ~= "") then
            nxt = dec.paging.next
        end
    end
end

function get_token(ctx)
    local c
    local cfg = datasrc_config()
    if cfg ~= nil then
        c = cfg.credentials
    end

    if (c == nil or c.key == nil or 
        c.secret == nil or c.key == "" or c.secret == "") then
        return ""
    end

    local authurl = "https://graph.facebook.com/oauth/access_token"
    authurl = authurl .. "?client_id=" .. c.key .. "&client_secret=" .. c.secret .. "&grant_type=client_credentials"

    local resp, err = request(ctx, {['url']=authurl})
    if (err ~= nil and err ~= "") then
        return ""
    end
    
    local dec = json.decode(resp)
    if (dec == nil or dec.access_token == nil or dec.access_token == "") then
        return ""
    end

    return dec.access_token
end

function query_url(domain, token)
    if token == "" then
        return ""
    end

    local u = "https://graph.facebook.com/" .. api_version
    return u .. "/certificates?fields=domains&access_token=" .. token .. "&query=*." .. domain
end
