import flextag

flex_tag_string = "[[---- ai text response --\nHello World\n--]]"
flextag_dict = flextag.flex_to_dict(flex_tag_string)

print(flextag_dict)
