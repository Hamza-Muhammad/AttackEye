-- Copyright 2021 Jeff Foley. All rights reserved.
-- Use of this source code is governed by Apache 2 LICENSE that can be found in the LICENSE file.

name = "Searchcode"
type = "scrape"

function start()
    set_rate_limit(2)
end

function vertical(ctx, domain)
    for i=0,20 do
        local page, err = request(ctx, {['url']=build_url(domain, i)})
        if (err ~= nil and err ~= "") then
            log(ctx, "vertical request to service failed: " .. err)
            break
        end

        local found = find_names(ctx, page:gsub("<strong>", ""), domain)
        if not found then
            break
        end
    end
end

function build_url(domain, pagenum)
    return "https://searchcode.com/?q=." .. domain .. "&p=" .. pagenum
end

function find_names(ctx, content, domain)
    local names = find(content, subdomain_regex)
    if (names == nil or #names == 0) then
        return false
    end

    local found = false
    for _, name in pairs(names) do
        if in_scope(ctx, name) then
            found = true
            new_name(ctx, name)
        end
    end

    return found
end
