require 'active_record'
require_relative './models/gauge'
require_relative './models/gauges_measure'
require_relative './models/tweet'
require 'csv'

# connect to db
def db_configuration
  db_configuration_file = File.join(File.expand_path('..', __FILE__), 'db', 'config.yml')
  YAML.load(File.read(db_configuration_file))
end
ActiveRecord::Base.establish_connection(db_configuration["development"])
# read csv 2016
gauges2016 = CSV.read("./data/rainfall/2692_SP_2016_1.csv", { col_sep: ";" })
tweets = CSV.read("./data/tweetsGauge.csv", { col_sep: "\t" })

# add to database
gauges2016[1..gauges2016.length].each do |row|
  begin
    gauge = Gauge.where(cod: row[1]).first
    GaugesMeasure.create!( gauge_id: gauge.id,
                      measured_at: DateTime.strptime(row[6] ,"%Y-%m-%d %H:%M:%S"),
                      measure: row[7].gsub("\,", "\.").to_f)
  rescue
    Gauge.create!(city: row[0], cod: row[1], state: row[2], name: row[3], latitude: row[4], longitude: row[5])
    gauge = Gauge.where(cod: row[1]).first
    GaugesMeasure.create!( gauge_id: gauge.id,
                      measured_at: DateTime.strptime(row[6] ,"%Y-%m-%d %H:%M:%S"),
                      measure: row[7].gsub("\,", "\.").to_f)
  end
end
# add to database
tweets[1..tweets.length].each do |row|
  Tweet.create!(  id_str: row[1],
                  posted_at: DateTime.strptime(row[2] ,"%Y-%m-%d %H:%M:%S"),
                  latitude: row[4].gsub("\,", "\.").to_f,
                  longitude: row[3].gsub("\,", "\.").to_f,
                  rain_related: row[5],
                  gauge_id: row[6])
end
