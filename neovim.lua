return {
	{
		"folke/tokyonight.nvim",
		priority = 1000,
		opts = {
			style = "night",
			on_colors = function(colors)
				colors.bg = "#04080a"
				colors.bg_dark = "#030607"
				colors.bg_float = "#030607"
				colors.bg_sidebar = "#030607"
				colors.bg_statusline = "#030607"
				colors.bg_visual = "#12402e"
				colors.fg = "#d6f5e6"
				colors.fg_dark = "#b6e8d0"
				colors.fg_gutter = "#2e8f63"
				colors.border = "#4bffa5"
				colors.green = "#4bffa5"
				colors.cyan = "#4be0ff"
				colors.blue = "#4b9dff"
				colors.magenta = "#c77dff"
				colors.red = "#ff4d5e"
				colors.yellow = "#ffc061"
				colors.orange = "#ff8f4d"
			end,
		},
	},
	{
		"LazyVim/LazyVim",
		opts = {
			colorscheme = "tokyonight-night",
		},
	},
}
