#!/bin/env dls-python
"""A class for generating virtual dataset frames from sub-frames."""

from .vdsgenerator import VDSGenerator, SourceMeta
from .group import VirtualSource, VirtualTarget, VirtualMap
from .hyperslab import Hyperslab


class SubFrameVDSGenerator(VDSGenerator):

    """A class to generate Virtual Dataset frames from sub-frames."""

    # Default Values
    stripe_spacing = 10  # Pixel spacing between stripes in a module
    module_spacing = 10  # Pixel spacing between modules

    def __init__(self, path, prefix=None, files=None, output=None, source=None,
                 source_node=None, target_node=None, fill_value=None,
                 stripe_spacing=None, module_spacing=None,
                 log_level=None):
        """
        Args:
            path(str): Root folder to find raw files and create VDS
            prefix(str): Prefix of HDF5 files to generate from
                e.g. image_ for image_1.hdf5, image_2.hdf5, image_3.hdf5
            files(list(str)): List of HDF5 files to generate from
            output(str): Name of VDS file.
            source(dict): Height, width, data_type and frames for source data
                Provide this to create a VDS for raw files that don't exist yet
            source_node(str): Data node in source HDF5 files
            target_node(str): Data node in VDS file
            fill_value(int): Fill value for spacing
            stripe_spacing(int): Spacing between stripes in module
            module_spacing(int): Spacing between modules
            log_level(int): Logging level (off=3, info=2, debug=1) -
                Default is info

        """
        super(SubFrameVDSGenerator, self).__init__(
            path, prefix, files, output, source, source_node, target_node,
            fill_value, log_level)

        # Overwrite default values with arguments, if given
        if stripe_spacing is not None:
            self.stripe_spacing = stripe_spacing
        if module_spacing is not None:
            self.module_spacing = module_spacing

    def process_source_datasets(self):
        """Grab data from the given HDF5 files and check for consistency.

        Returns:
            Source: Number of datasets and the attributes of them (frames,
                height width and data type)

        """
        data = self.grab_metadata(self.datasets[0])
        frames = [data["frames"]]
        for dataset in self.datasets[1:]:
            temp_data = self.grab_metadata(dataset)
            frames.append(temp_data["frames"])
            for attribute, value in data.items():
                if temp_data[attribute] != value:
                    raise ValueError("Files have mismatched "
                                     "{}".format(attribute))

        source = SourceMeta(frames=data['frames'], height=data['height'],
                            width=data['width'], dtype=data['dtype'])

        self.logger.debug("Source metadata retrieved:\n"
                          "  Frames: %s\n"
                          "  Height: %s\n"
                          "  Width: %s\n"
                          "  Data Type: %s", frames, *source[1:])
        return source

    def construct_vds_spacing(self):
        """Construct list of spacing between each stripe.

        Returns:
            VDS: Dataset spacing of virtual data set

        """
        stripes = len(self.datasets)
        spacing = [0] * stripes
        for idx in range(0, stripes - 1, 2):
            spacing[idx] = self.stripe_spacing
        for idx in range(1, stripes, 2):
            spacing[idx] = self.module_spacing
        # We don't want the final stripe to have a gap afterwards
        spacing[-1] = 0

        return spacing

    def create_vds_maps(self, source_meta):
        """Create a list of VirtualMaps of raw data to the VDS.

        Args:
            source_meta(SourceMeta): Source attributes

        Returns:
            list(VirtualMap): Maps describing links between raw data and VDS

        """
        source_shape = source_meta.frames + (source_meta.height,
                                             source_meta.width)
        spacing = self.construct_vds_spacing()
        target_height = source_meta.height * len(self.datasets) + sum(spacing)
        target_shape = source_meta.frames + (target_height,
                                             source_meta.width)
        self.logger.debug("VDS metadata:\n"
                          "  Shape: %s\n"
                          "  Spacing: %s", target_shape, spacing)

        vds = VirtualTarget(self.output_file, self.target_node,
                            shape=target_shape)

        map_list = []
        current_position = 0
        for idx, dataset in enumerate(self.datasets):
            v_source = VirtualSource(dataset, self.source_node,
                                     shape=source_shape)

            start = current_position
            stop = start + source_meta.height + spacing[idx]
            current_position = stop

            # Hyperslab: All frames for each axis,
            #            Height bounds of stripe,
            #            Entire width
            hyperslab = Hyperslab([self.FULL_SLICE] * len(source_meta.frames),
                                  slice(start, stop),
                                  self.FULL_SLICE)

            v_target = vds[hyperslab.tuple]
            v_map = VirtualMap(v_source, v_target, dtype=source_meta.dtype)

            self.logger.debug("Mapping dataset %s to %s of %s.",
                              dataset.split("/")[-1], hyperslab, self.name)
            map_list.append(v_map)

        return map_list
