# -*- coding:utf-8 -*- #
#
# Anomaly Detection Framework
# Copyright (C) 2018 Bluekiri BigData Team <bigdata@bluekiri.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

from anomalydetection.backend.stream import FileObservable

from anomalydetection.backend.engine.builder import EngineBuilderFactory
from anomalydetection.backend.entities.json_input_message_handler import \
    InputJsonMessageHandler
from anomalydetection.backend.interactor.batch_engine import BatchEngineInteractor


if __name__ == "__main__":

    interactor = BatchEngineInteractor(
        FileObservable(sys.argv[1]),
        EngineBuilderFactory.get_ema().set_window(50).set_threshold(2.5),
        InputJsonMessageHandler())

    data = interactor.process()
    [print(str(m)) for m in data]
