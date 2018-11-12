require 'active_record'
require_relative './app/models/gauge'
require_relative './app/models/gauges_measure'
require_relative './app/models/tweet'
require_relative './app/models/infos_in_hour'
require 'csv'

# connect to db
def db_configuration
  db_configuration_file = File.join(File.expand_path('..', __FILE__), 'config', 'database.yml')
  YAML.load(File.read(db_configuration_file))
end
ActiveRecord::Base.establish_connection(db_configuration["development"])
# read csv 2016
gauges2016 = CSV.read("./data/rainfall/2692_SP_2016_1.csv", { col_sep: ";" })
tweets = CSV.read("./data/tweetsGauge.csv", { col_sep: "\t" })

puts "adding gauges and measures..."
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

puts "adding tweets..."
# add to database
tweets[1..tweets.length].each do |row|
  Tweet.create!(  id_str: row[1],
                  posted_at: DateTime.strptime(row[2] ,"%Y-%m-%d %H:%M:%S"),
                  latitude: row[4].gsub("\,", "\.").to_f,
                  longitude: row[3].gsub("\,", "\.").to_f,
                  rain_related: (row[5].to_s == "True"),
                  gauge_id: row[6])
end

puts "adding info per hour..."
# add to database
(1..31).to_a.each do |day|
  (0..23).to_a.each do |hour|
    Gauge.all.each do |gauge|
      hour_tweets = Tweet.where(gauge_id: gauge.cod).
                          where('posted_at > ?', Time.new(2016, 1, day, hour, 0, 0)).
                          where('posted_at <= ?', Time.new(2016, 1, day, (hour+1), 0, 0))

      hour_gauges_measures = GaugesMeasure.where(gauge_id: gauge.cod).
                                            where('measured_at > ?', Time.new(2016, 1, day, hour, 0, 0)).
                                            where('measured_at <= ?', Time.new(2016, 1, day, (hour+1), 0, 0))

      InfosInHour.create!(gauge_id: gauge.cod,
                          hour: Time.new(2016, 1, day, hour, 0, 0),
                          all_tweets: hour_tweets.count,
                          related_tweets: hour_tweets.where(rain_related: true).count,
                          gauge_measures: hour_gauges_measures.pluck(:measure).sum)
    end
  end
end
