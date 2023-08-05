from os.path import expanduser

# General parameters
home_dir = expanduser("~") + "/" # Home dir (e.g: "/home/your_user_name/").
bitcoin_tools_dir = home_dir + 'bitcoin_tools/'  # Bitcoin_tools data dir.
address_vault = bitcoin_tools_dir + "bitcoin_addresses/"  # Address vault .

#  STATUS parameters
default_coin = 'bitcoin'
chainstate_path = home_dir + ".bitcoin/chainstate"  # Path to the chainstate.
data_path = bitcoin_tools_dir + "data/"  # Data storage path (for IO).
figs_path = bitcoin_tools_dir + "figs/"  # Figure store dir, where images from analysis will be stored.
estimated_data_dir = bitcoin_tools_dir + 'estimation_data/'  # Data for non-profitability with estimations