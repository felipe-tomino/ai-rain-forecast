class CreateInfosInHours < ActiveRecord::Migration
  def change
    create_table :infos_in_hours do |t|
      t.belongs_to :gauge, index: true
      t.datetime :time
      t.integer :all_tweets
      t.integer :related_tweets
      t.float :gauge_measures
    end
    create_table :infos_in_half_hours do |t|
      t.belongs_to :gauge, index: true
      t.datetime :time
      t.integer :all_tweets
      t.integer :related_tweets
      t.float :gauge_measures
    end
  end
end
