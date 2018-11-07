class CreateGaugesAndTweets < ActiveRecord::Migration
  def change
    create_table :gauges do |t|
      t.string :cod
      t.string :city
      t.string :state
      t.string :name
      t.string :latitude
      t.string :longitude
    end

    create_table :gauges_measures do |t|
      t.belongs_to :gauge, index: true
      t.datetime :measured_at
      t.float :measure
    end

    create_table :tweets do |t|
      t.belongs_to :gauge, index: true
      t.string :id_str
      t.datetime :posted_at
      t.string :latitude
      t.string :longitude
      t.boolean :rain_related
    end
  end
end
