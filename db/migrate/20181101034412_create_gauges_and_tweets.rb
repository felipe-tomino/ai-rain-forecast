class CreateGaugesAndTweets < ActiveRecord::Migration[5.2]
  def change
    create_table :gauges do |t|
      t.string :cod
      t.string :city
      t.string :state
      t.string :name
      t.string :latitude
      t.string :longitude

      t.timestamps
    end

    create_table :gauges_measures do |t|
      t.belongs_to :gauge, index: true
      t.datetime :measured_at
      t.float :measure

      t.timestamps
    end

    create_table :tweets do |t|
      t.belongs_to :gauge, index: true
      t.string :id_str
      t.datetime :posted_at
      t.string :latitude
      t.string :longitude
      t.string :rain_related

      t.timestamps
    end
  end
end
