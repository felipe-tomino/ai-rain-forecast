ENV['SINATRA_ENV'] ||= "development"

require 'bundler/setup'
Bundler.require(:default, ENV['SINATRA_ENV'])

# connect to db
def db_configuration
  db_configuration_file = 'config/database.yml'
  YAML.load(File.read(db_configuration_file))
end
ActiveRecord::Base.establish_connection(db_configuration[ENV['SINATRA_ENV']])

require './app/controllers/application_controller'
require_all 'app'
