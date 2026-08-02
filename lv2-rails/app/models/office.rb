class Office < ApplicationRecord
  has_many :restaurants, dependent: :destroy

  validates :name, presence: true, uniqueness: true
end
